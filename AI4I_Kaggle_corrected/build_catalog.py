"""Build an AI4I–Kaggle class reference catalog, NOT paired training data."""
import argparse
import csv
import hashlib
import json
import math
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODES = ('TWF', 'HDF', 'PWF', 'OSF', 'RNF')
EXPECTED = dict(zip(MODES, (46,115,95,98,1)))
PHOTO_COUNTS = dict(zip(MODES, (22,13,4,40,0)))
RAW_SHA = 'dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e'
INDEX_SHA = '793b467d20d7d492f67cc6ff9e156cbe32cc3b133826d86da4d1b3ca14a4d32f'
ZIP_SHA = 'd30ffdcdcda1258ac95d89dd90539fe7ffd7b398e693ada652b4f63c073c9b28'

def check(condition, message):
    if not condition:
        raise ValueError(message)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write(p, rows, fields):
    with p.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

def image_audit(archive):
    check(sha(archive) == ZIP_SHA, 'Original Kaggle ZIP differs from previously audited archive')
    images = read(HERE/'image_mapping_234.csv')
    associations = read(HERE/'class_associations_79.csv')
    photos = {r['image_reference']: r for r in images}
    check(len(images) == len(photos) == 234, 'Unexpected photo population')
    with zipfile.ZipFile(archive) as z:
        for name, r in photos.items():
            check(hashlib.sha256(z.read(name)).hexdigest() == r['image_sha256'], 'Photo hash mismatch: '+name)
            check(r['confirmed_failure_type'] == 'UNKNOWN' and r['include_in_supervised_training']=='false', 'Unverified photo label or eligibility changed')
    check(len(associations)==79 and len({(r['failure_type'],r['image_reference']) for r in associations})==79, 'Unexpected associations')
    for r in associations:
        p = photos[r['image_reference']]
        check(r['image_sha256']==p['image_sha256'] and p['source_review_status']=='provisional_candidate', 'Association includes invalid image')
        check(r['verified_failure_label']=='UNKNOWN' and r['same_event_pair']=='false' and r['training_eligible']=='false', 'Association claims unsupported verification')
    check(all(sum(r['failure_type']==m for r in associations)==PHOTO_COUNTS[m] for m in MODES), 'Photo counts changed')
    return images, associations

def sensor_audit(raw, index):
    check(sha(raw)==RAW_SHA, 'AI4I raw CSV differs from previously audited original')
    check(sha(index)==INDEX_SHA, 'AI4I index differs from previously audited original')
    original, eligible = read(raw), read(index)
    by_id = {r['UDI']:r for r in original}
    check(len(original)==len(by_id)==10000 and len(eligible)==len({r['original_udi'] for r in eligible})==9973, 'Unexpected AI4I population')
    excluded = [r for r in original if int(r['Machine failure']) != int(any(r[m]=='1' for m in MODES))]
    check(len(excluded)==27 and set(by_id)-{r['original_udi'] for r in eligible}=={r['UDI'] for r in excluded}, 'Original quarantine changed')
    rows=[]
    for item in eligible:
        r=by_id[item['original_udi']]
        check(all(r[m]==item[f'source_{m}_label_not_a_predictor'] for m in MODES), 'Mode flag mismatch')
        check(r['Machine failure']==item['original_machine_failure_label_not_a_predictor'], 'Overall label mismatch')
        modes=[m for m in MODES if r[m]=='1']
        check('|'.join(modes)==item['source_positive_failure_modes_pipe_separated'], 'Mode index mismatch')
        rows.append({**r,'original_stage5_split':item['original_stage5_split'], 'failure_type_memberships':'|'.join(modes), 'temperature_difference_K':round(float(r['Process temperature [K]'])-float(r['Air temperature [K]']),6), 'mechanical_power_W':round(float(r['Torque [Nm]'])*float(r['Rotational speed [rpm]'])*2*math.pi/60,6), 'wear_torque_min_Nm':float(r['Tool wear [min]'])*float(r['Torque [Nm]']), 'source_kind':'PUBLISHER_SYNTHETIC_TABULAR', 'verified_photo_event_link':'false'})
    check(Counter(m for r in rows for m in MODES if r[m]=='1')==EXPECTED, 'AI4I class counts changed')
    return rows,excluded

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,default=Path('.'))
    ap.add_argument('--images-zip',type=Path,required=True)
    ap.add_argument('--images-only-audit',action='store_true')
    args=ap.parse_args()
    images,assoc=image_audit(args.images_zip)
    if args.images_only_audit:
        print(json.dumps({'status':'ORIGINAL_PHOTO_REFERENCE_AUDIT_PASSED','photo_hashes_checked':len(images),'association_rows':len(assoc)},indent=2));return
    raw=args.project/'data/raw/ai4i2020.csv'
    index=args.project/'data/processed/five_mode_image_annotation/original_ai4i_9973_eligible_five_mode_source_index.csv'
    sensors,excluded=sensor_audit(raw,index)
    out=args.project/'data/processed/ai4i_kaggle_class_catalog'
    if out.exists(): raise FileExistsError(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.ai4i-kaggle-catalog-',dir=out.parent))
    try:
        write(temp/'all_ai4i_records.csv',sensors,list(sensors[0]))
        write(temp/'excluded_ai4i_records.csv',excluded,list(excluded[0]))
        write(temp/'all_photo_annotations.csv',images,list(images[0]))
        write(temp/'all_class_associations.csv',assoc,list(assoc[0]))
        shutil.copyfile(HERE/'failure_type_bridge.csv',temp/'failure_type_bridge.csv')
        coverage=[]
        for m in MODES:
            d=temp/m;d.mkdir()
            sr=[r for r in sensors if r[m]=='1']
            ar=[r for r in assoc if r['failure_type']==m]
            visual=[r for r in ar if r['association_kind']!='EQUIPMENT_CONTEXT_ONLY']
            context=[r for r in ar if r['association_kind']=='EQUIPMENT_CONTEXT_ONLY']
            write(d/'ai4i_labeled_records.csv',sr,list(sensors[0]))
            write(d/'photo_visual_hypotheses_and_analogies.csv',visual,list(assoc[0]))
            write(d/'photo_equipment_context_only.csv',context,list(assoc[0]))
            coverage.append({'failure_type':m,'ai4i_positive_records':len(sr),'photo_visual_hypotheses_or_analogies':len(visual),'equipment_context_only':len(context),'verified_photo_labels':0,'verified_same_event_pairs':0})
        write(temp/'coverage.csv',coverage,list(coverage[0]))
        report={'status':'CLASS_REFERENCE_CATALOG_NOT_PAIRED_DATASET','ai4i_rows':len(sensors),'excluded_ai4i_rows':len(excluded),'photo_hashes_verified':len(images),'class_reference_associations':len(assoc),'coverage':coverage,'verified_failure_photos':0,'verified_same_event_pairs':0,'full_multimodal_ready':False,'source_sha256':{'ai4i':RAW_SHA,'index':INDEX_SHA,'kaggle_zip':ZIP_SHA},'limitations':['AI4I is synthetic tabular data; no physical machine or timestamp link to Kaggle photographs.','Photo hypotheses and context are not confirmed causal failure labels.','No photo bytes redistributed; resolve image references against the original ZIP.','SCANIA and MATWI excluded. No new training labels, splits, models, or fabricated pairs.']}
        (temp/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        temp.rename(out)
    finally:
        if temp.exists():shutil.rmtree(temp)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
