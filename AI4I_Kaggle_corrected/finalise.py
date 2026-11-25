"""Canonical AI4I-Kaggle dataset: real photo bytes once, class-level reference links only."""
import argparse, json, shutil, tempfile, zipfile, hashlib
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict
from build_catalog import check, read, write, sha, MODES, EXPECTED, image_audit, sensor_audit
HERE=Path(__file__).resolve().parent

def build(archive, out, project, photos_only=False):
    if out.exists(): raise FileExistsError(f'Will not overwrite {out}')
    photos, associations=image_audit(archive)
    index=read(HERE/'ai4i_kaggle_canonical_photo_index.csv')
    grouped=defaultdict(set)
    for r in photos: grouped[r['image_sha256']].add(r['image_reference'])
    check(len(index)==len({r['image_id'] for r in index})==len(grouped)==225,'Canonical count mismatch')
    check(set(grouped)=={r['image_id'] for r in index},'Canonical population mismatch')
    assoc_by_key={(r['image_sha256'],r['failure_type']):r['association_kind'] for r in associations}
    check(len(assoc_by_key)==79,'Unexpected content-level association count')
    rows,excluded=([],[]) if photos_only else sensor_audit(project/'data/raw/ai4i2020.csv',project/'data/processed/five_mode_image_annotation/original_ai4i_9973_eligible_five_mode_source_index.csv')
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=Path(tempfile.mkdtemp(prefix='.canonical-',dir=out.parent))
    try:
        links=[]; registry=[]
        with zipfile.ZipFile(archive) as z:
            for r in index:
                h=r['image_id']; ref=r['canonical_original_reference']; disposition=r['review_disposition']
                check(ref in grouped[h] and set(r['original_references'].split('|'))==grouped[h],'Original reference mismatch '+h)
                check(disposition in ('QUARANTINE','RETAIN_FOR_EXPLORATORY_REFERENCE'),'Unknown disposition')
                check(r['verified_ai4i_failure_label']=='UNKNOWN' and r['ai4i_supervised_image_eligible']=='false' and r['same_event_pair']=='false','Unsupported label')
                folder='quarantine' if disposition=='QUARANTINE' else 'photos'
                dest=Path(folder)/(h+PurePosixPath(ref).suffix.lower())
                p=tmp/dest; p.parent.mkdir(exist_ok=True); p.write_bytes(z.read(ref)); check(sha(p)==h,'Photo content mismatch')
                entry={**r,'canonical_local_path':dest.as_posix()}; registry.append(entry)
                for m in MODES:
                    kind=r[m+'_association']; expected=assoc_by_key.get((h,m),'NO_SUPPORTED_ASSOCIATION')
                    check(kind==expected,'Class mapping mismatch '+h+' '+m)
                    check(r[m+'_verified_target']=='UNKNOWN','Unexpected target')
                    if disposition!='QUARANTINE' and kind!='NO_SUPPORTED_ASSOCIATION':
                        links.append({'failure_type':m,'image_id':h,'photo_path_from_dataset_root':dest.as_posix(),'association_kind':kind,'verified_target':'UNKNOWN','training_eligible':'false','same_event_pair':'false'})
        check(Counter(r['review_disposition'] for r in registry)=={'RETAIN_FOR_EXPLORATORY_REFERENCE':219,'QUARANTINE':6},'Disposition counts')
        check(len(links)==79 and len({r['image_id'] for r in links})==78,'Association counts')
        write(tmp/'photo_index.csv',registry,list(registry[0])); write(tmp/'class_photo_links.csv',links,list(links[0]));
        shutil.copyfile(HERE/'failure_type_bridge.csv',tmp/'failure_type_bridge.csv')
        linked={r['image_id'] for r in links}
        unmapped=[r for r in registry if r['image_id'] not in linked and r['review_disposition']!='QUARANTINE']
        write(tmp/'unmapped_retained.csv',unmapped,list(registry[0]))
        coverage=[]
        for m in MODES:
            d=tmp/m; d.mkdir(); subset=[r for r in links if r['failure_type']==m]
            write(d/'photo_links.csv',subset,list(links[0]))
            sr=[r for r in rows if r[m]=='1']
            if not photos_only: write(d/'ai4i_measurements.csv',sr,list(rows[0]))
            coverage.append({'failure_type':m,'ai4i_records':None if photos_only else len(sr),'photo_hypotheses_or_analogies':sum(r['association_kind']!='EQUIPMENT_CONTEXT_ONLY' for r in subset),'equipment_context':sum(r['association_kind']=='EQUIPMENT_CONTEXT_ONLY' for r in subset),'confirmed_photo_labels':0})
        if not photos_only:
            write(tmp/'all_ai4i_records.csv',rows,list(rows[0])); write(tmp/'excluded_ai4i_records.csv',excluded,list(excluded[0]))
            (tmp/'NO_FAILURE').mkdir(); write(tmp/'NO_FAILURE'/'ai4i_measurements.csv',[r for r in rows if r['Machine failure']=='0'],list(rows[0]))
        write(tmp/'coverage.csv',coverage,list(coverage[0]))
        check(len(list((tmp/'photos').iterdir()))==219 and len(list((tmp/'quarantine').iterdir()))==6,'File counts')
        check(all(sha(tmp/r['photo_path_from_dataset_root'])==r['image_id'] for r in links),'Broken class link')
        report={'status':'PHOTO_SIDE_VALIDATED_ONLY' if photos_only else 'CANONICAL_CLASS_ORGANIZED_EXPLORATORY_DATASET','ai4i_rows':None if photos_only else len(rows),'excluded_ai4i_rows':None if photos_only else len(excluded),'original_photo_references':234,'unique_photo_files':225,'retained_photo_files':219,'quarantined_photo_files':6,'class_links':len(links),'unique_linked_photos':len(linked),'unmapped_retained_photos':len(unmapped),'coverage':coverage,'verified_photo_labels':0,'verified_same_event_pairs':0,'full_five_mode_mapping_validated':False,'photo_training_eligible':False,'source_data_modified':False,'limitations':['AI4I synthetic tabular observations; no physical event pairing.','Photo links are analogies, hypotheses or equipment context, never verified targets.','PWF context only; RNF missing.','Photo reuse rights unverified; local processing only.','SCANIA and MATWI excluded.']}
        (tmp/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8'); tmp.rename(out)
    finally:
        if tmp.exists(): shutil.rmtree(tmp)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--project',type=Path,default=Path('.')); ap.add_argument('--images-zip',type=Path,required=True); ap.add_argument('--out',type=Path); ap.add_argument('--photos-only',action='store_true'); a=ap.parse_args()
    out=a.out or a.project/'data/processed'/('ai4i_kaggle_canonical_photo_test' if a.photos_only else 'ai4i_kaggle_multimodal_canonical')
    print(json.dumps(build(a.images_zip,out,a.project,a.photos_only),indent=2)); print('Output:',out)
