"""Fail-closed audit and corrected reference view. No new sources, no training labels."""
import argparse, csv, hashlib, json, shutil, tempfile, zipfile
from collections import Counter
from pathlib import Path
from build_catalog import sensor_audit, image_audit, RAW_SHA, INDEX_SHA, ZIP_SHA, MODES, EXPECTED
from finalise import build
HERE=Path(__file__).resolve().parent
PINS={
'image_mapping_234.csv':'90178db51332f3b4c9f92f667e15cf54c0a859ea62108ec0999c92a895e229e9',
'class_associations_79.csv':'00230cae5040d4335893f8c6d1714acdc607ebeb7300770e0f79c08f2338c533',
'ai4i_kaggle_canonical_photo_index.csv':'8dba653567ca91f226019ff8ce4a6bd8af17942a04702c5bd4813b9880064f7f',
'failure_type_bridge.csv':'74a6989d69ffa02d639f21cae162f4dc2c5c5b9181bbea568447b6b611099999',
'media_review_225.csv':'26f987df14a42ab91a8b9dfbb54efb98248e5e8e1c6cac7173335c167104d73e',
'AI4I_Kaggle_decisions_semantiques_55.csv':'a1d72ed17260383840940b8db955abf66a85a86e1801a564810e4387d0d319c5'}
SPLITS={'train':6981,'validation':1497,'test':1495}
KINDS={'TWF':'COMPONENT_WEAR_ANALOGY_ONLY','HDF':'WEAK_CAUSAL_HYPOTHESIS','PWF':'EQUIPMENT_CONTEXT_ONLY','OSF':'WEAK_CAUSAL_HYPOTHESIS'}
STRICT={'TWF':16,'HDF':11,'PWF':4,'OSF':24,'RNF':0}
MEDIA={'PHOTO_APPEARANCE':135,'ANNOTATED_OR_COMPOSITE_PHOTO_APPEARANCE':41,'MEDIA_TYPE_UNCERTAIN':37,'RENDER_OR_TECHNICAL_ILLUSTRATION_APPEARANCE':12}
BASE_PREDICTORS=['Type','Air temperature [K]','Process temperature [K]','Rotational speed [rpm]','Torque [Nm]','Tool wear [min]']
def require(ok,msg):
    if not ok: raise ValueError(msg)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csv_read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:
        rd=csv.DictReader(f); fields=rd.fieldnames or []; rows=list(rd)
    require(bool(fields) and len(fields)==len(set(fields)) and all(k for k in fields),f'Invalid header: {p}')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows),f'Malformed rows: {p}')
    return fields,rows
def write(p,fields,rows):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def same_csv(p,q):
    require(csv_read(p)==csv_read(q),f'CSV differs from trusted reconstruction: {p}')
def compare_rows(p,fields,rows):
    require(csv_read(p)==(fields,[{k:str(v) for k,v in r.items()} for r in rows]),f'Unexpected rows/schema/order: {p}')
def safe_file(root,relative):
    p=root/relative
    require(not Path(relative).is_absolute() and '\\' not in relative and '..' not in Path(relative).parts and p.resolve().is_relative_to(root.resolve()),f'Unsafe path: {relative}')
    require(p.is_file() and not any(x.is_symlink() for x in [p,*p.parents] if x!=root and x.is_relative_to(root)),f'Missing/symlink path: {relative}')
    return p
def encoding(p):
    with p.open('rb') as f: b=f.read(16)
    if b[:3]==b'\xff\xd8\xff': return 'JPEG','.jpg'
    if b[:8]==b'\x89PNG\r\n\x1a\n': return 'PNG','.png'
    if b[:4]==b'RIFF' and b[8:12]==b'WEBP': return 'WEBP','.webp'
    raise ValueError(f'Unrecognized original image format: {p}')
def validate(root,archive,project,photos_only=False):
    for name,digest in PINS.items(): require(sha(HERE/name)==digest,f'Locked annotation asset changed: {name}')
    require(root.is_dir(),'Canonical dataset not found')
    # Rebuild from exact approved bytes and pinned annotations, not from mutable local manifests.
    with tempfile.TemporaryDirectory(prefix='ai4i-kaggle-reference-') as t:
        ref=Path(t)/'ref'; build(archive,ref,project,photos_only=photos_only)
        common=['photo_index.csv','class_photo_links.csv','unmapped_retained.csv','failure_type_bridge.csv',*[f'{m}/photo_links.csv' for m in MODES]]
        if not photos_only: common+=['all_ai4i_records.csv','excluded_ai4i_records.csv','coverage.csv','NO_FAILURE/ai4i_measurements.csv',*[f'{m}/ai4i_measurements.csv' for m in MODES]]
        for name in common: same_csv(safe_file(root,name),ref/name)
        if not photos_only:
            actual=json.loads(safe_file(root,'report.json').read_text(encoding='utf-8'))
            expected=json.loads((ref/'report.json').read_text(encoding='utf-8'))
            require(actual==expected,'Canonical report differs from clean rebuild')
    ixfields,index=csv_read(root/'photo_index.csv'); lf,links=csv_read(root/'class_photo_links.csv'); mf,media=csv_read(HERE/'media_review_225.csv'); df,decisions=csv_read(HERE/'AI4I_Kaggle_decisions_semantiques_55.csv')
    idx={r['image_id']:r for r in index}; med={r['image_id']:r for r in media}
    require(len(index)==len(idx)==len(media)==len(med)==225 and idx.keys()==med.keys(),'Image population changed')
    require(Counter(r['media_review'] for r in media)==MEDIA,'Media types changed')
    expected_paths=set();formats=[]; eligible=set()
    for h,r in idx.items():
        m=med[h];p=safe_file(root,r['canonical_local_path']); expected_paths.add(p.relative_to(root).as_posix())
        require(sha(p)==h,'Image hash mismatch: '+h)
        require(r['reuse_rights']==m['reuse_rights']=='UNVERIFIED' and r['verified_ai4i_failure_label']==m['verified_ai4i_failure_label']=='UNKNOWN' and r['ai4i_supervised_image_eligible']==m['supervised_training_eligible']==r['same_event_pair']=='false','Unsupported image claim')
        require(m['canonical_disposition']==r['review_disposition'] and m['original_reference']==r['canonical_original_reference'],'Media lineage mismatch')
        keep=m['media_review']=='PHOTO_APPEARANCE' and r['review_disposition']=='RETAIN_FOR_EXPLORATORY_REFERENCE'
        require(m['strict_photo_reference_eligible']==str(keep).lower(),'Media eligibility mismatch')
        if keep: eligible.add(h)
        fmt,ext=encoding(p); match=p.suffix.lower() in ({'.jpg','.jpeg'} if fmt=='JPEG' else {ext})
        formats.append({'image_id':h,'canonical_local_path':r['canonical_local_path'],'actual_encoding':fmt,'recommended_extension':ext,'filename_extension_matches':str(match).lower(),'strict_photo_reference_eligible':str(keep).lower()})
    actual_paths={p.relative_to(root).as_posix() for d in ('photos','quarantine') for p in (root/d).rglob('*') if p.is_file()}
    require(actual_paths==expected_paths,'Unexpected/missing physical image files')
    seen=set(); strict=[]; excluded=[]
    for r in links:
        h=r['image_id']; mode=r['failure_type']; k=(h,mode)
        require(k not in seen and h in idx and mode in KINDS and r['association_kind']==KINDS[mode],'Invalid/duplicate class association')
        seen.add(k); i=idx[h]
        require(i['review_disposition']=='RETAIN_FOR_EXPLORATORY_REFERENCE' and r['photo_path_from_dataset_root']==i['canonical_local_path'] and i[mode+'_association']==r['association_kind'],'Link lineage mismatch')
        require(r['verified_target']=='UNKNOWN' and r['training_eligible']==r['same_event_pair']=='false','Unsupported target/event')
        item={**r,'media_review':med[h]['media_review'],'strict_photo_reference_eligible':str(h in eligible).lower()}
        (strict if h in eligible else excluded).append(item)
    require(len(links)==79 and len(eligible)==133 and len(strict)==55 and len(excluded)==24,'Unexpected coverage')
    require({m:sum(r['failure_type']==m for r in strict) for m in MODES}==STRICT,'Strict class coverage changed')
    selected=[dict(r,media_review=med[r['image_id']]['media_review']) for r in index if r['image_id'] in eligible]
    fields=lf+['media_review','strict_photo_reference_eligible']; keys={(r['image_id'],r['failure_type']):r for r in strict}
    dkeys=set()
    for d in decisions:
        k=(d['image_sha256'],d['failure_type']); require(k in keys and k not in dkeys,'Semantic decision mismatch'); dkeys.add(k); r=keys[k]
        require(d['relative_photo_path']==r['photo_path_from_dataset_root'] and d['prior_association_kind']==r['association_kind'] and d['verified_failure_label']=='UNKNOWN' and d['allowed_as_supervised_target']==d['same_event_pair']=='false' and d['rights_status']=='UNVERIFIED','Invalid semantic evidence')
    require(dkeys==keys.keys(),'Incomplete semantic decisions')
    # Check existing legacy view if present; do not silently repair a corrupt one.
    legacy=root/'photo_only_review'
    if legacy.exists():
        for name,header,rows in [('photo_index.csv',ixfields+['media_review'],selected),('class_photo_links.csv',fields,strict),('excluded_class_photo_links.csv',fields,excluded),('media_review_225.csv',mf,media),*[(f'{m}/photo_links.csv',fields,[r for r in strict if r['failure_type']==m]) for m in MODES]]:
            compare_rows(safe_file(root,'photo_only_review/'+name),header,rows)
    sensors=[]; split_counts={}; rnfs={}
    if not photos_only:
        sf,sensors=csv_read(root/'all_ai4i_records.csv')
        _,bad=csv_read(root/'excluded_ai4i_records.csv'); ids={r['UDI'] for r in sensors}; badids={r['UDI'] for r in bad}
        require(len(sensors)==len(ids)==9973 and len(bad)==len(badids)==27 and not ids&badids,'Invalid AI4I quarantine')
        split_counts=dict(Counter(r['original_stage5_split'] for r in sensors)); require(split_counts==SPLITS,'Stage 5 split changed')
        require(Counter(r['Machine failure'] for r in sensors)=={'0':9643,'1':330},'AI4I global labels changed')
        require(all(r['verified_photo_event_link']=='false' and r['source_kind']=='PUBLISHER_SYNTHETIC_TABULAR' for r in sensors),'Unsupported source claim')
        rnfs={s:sum(r['RNF']=='1' and r['original_stage5_split']==s for r in sensors) for s in SPLITS}
    return dict(index=index,selected=selected,strict=strict,excluded=excluded,formats=formats,decisions=decisions,sensors=sensors,split_counts=split_counts,rnfs=rnfs,ixfields=ixfields,fields=fields,df=df)
def run(root,archive,project,out,photos_only=False):
    require(not out.exists(),f'Refusing overwrite: {out}')
    data=validate(root,archive,project,photos_only)
    # Only publish after every check has passed. Original source and prior views remain untouched.
    out.parent.mkdir(parents=True,exist_ok=True); tmp=Path(tempfile.mkdtemp(prefix='.corrected-',dir=out.parent))
    try:
        for name,rows,fields in [('photo_index.csv',data['selected'],data['ixfields']+['media_review']),('class_photo_links.csv',data['strict'],data['fields']),('excluded_class_photo_links.csv',data['excluded'],data['fields']),('image_formats_225.csv',data['formats'],list(data['formats'][0])),('semantic_decisions_55.csv',data['decisions'],data['df'])]: write(tmp/name,fields,rows)
        cov=[{'failure_type':m,'ai4i_records':None if photos_only else EXPECTED[m],'strict_photo_links':STRICT[m],'confirmed_photo_labels':0,'equipment_context_only':STRICT[m] if m=='PWF' else 0} for m in MODES]
        write(tmp/'coverage.csv',list(cov[0]),cov)
        for m in MODES: write(tmp/m/'photo_links.csv',data['fields'],[r for r in data['strict'] if r['failure_type']==m])
        if not photos_only:
            for s in SPLITS:
                rows=[r for r in data['sensors'] if r['original_stage5_split']==s]
                fields=['UDI','original_stage5_split',*BASE_PREDICTORS,'Machine failure',*MODES]
                write(tmp/'eligible_ai4i'/f'{s}.csv',fields,[{k:r[k] for k in fields} for r in rows])
        policy={'authoritative_view':'corrected_review_v1','image_paths_relative_to':str(root.resolve()),'legacy_ai4i_phase2_splits_allowed':False,'legacy_photo_view_and_79_link_bridge':'historical only; use corrected coverage.csv','base_predictor_allowlist':BASE_PREDICTORS,'identifiers_not_predictors':['UDI','original_stage5_split'],'target_columns':['Machine failure',*MODES],'photo_training_eligible':False,'models_authorized':False,'source_policy':'AI4I + original Kaggle only; SCANIA separate; MATWI excluded','rights':'UNVERIFIED','data_kind':'publisher-synthetic tabular observations; no timestamped trajectories','format_policy':'use actual_encoding in image_formats_225.csv; original suffixes and bytes preserved'}
        (tmp/'data_policy.json').write_text(json.dumps(policy,indent=2),encoding='utf-8')
        report={'status':'CORRECTED_PHOTO_SIDE_PASS_ONLY' if photos_only else 'CORRECTED_FULL_TECHNICAL_PASS_EXPLORATORY_ONLY','full_ai4i_rebuild_verified':not photos_only,'source_sha256':{'kaggle_zip':ZIP_SHA,'ai4i':None if photos_only else RAW_SHA,'index':None if photos_only else INDEX_SHA},'split_counts':data['split_counts'],'rnf_positive_by_split':data['rnfs'],'verified_image_hashes':225,'strict_photo_references':133,'strict_links':55,'format_mismatches':[r for r in data['formats'] if r['filename_extension_matches']=='false'],'coverage':cov,'confirmed_photo_labels':0,'verified_event_pairs':0,'full_five_mode_mapping_validated':False,'supervised_multimodal_ready':False,'output_sha256':{p.relative_to(tmp).as_posix():sha(p) for p in sorted(tmp.rglob('*')) if p.is_file()}}
        (tmp/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');tmp.rename(out)
    finally:
        if tmp.exists(): shutil.rmtree(tmp)
    return report
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--project',type=Path,default=Path('.'));ap.add_argument('--images-zip',type=Path,required=True);ap.add_argument('--dataset',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--photos-only',action='store_true');a=ap.parse_args();root=(a.dataset or a.project/'data/processed/ai4i_kaggle_multimodal_canonical').resolve();out=a.out or root/'corrected_review_v1'; print(json.dumps(run(root,a.images_zip,a.project,out,a.photos_only),indent=2))
