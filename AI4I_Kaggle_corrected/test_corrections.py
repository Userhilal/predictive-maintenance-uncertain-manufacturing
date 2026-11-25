"""Negative tests against real source-derived photo manifests, never training data."""
import argparse,csv,json,shutil,tempfile
from pathlib import Path
from finalise import build
from validate_and_correct import run, csv_read, write, sha, HERE

def main(archive):
    results=[]
    with tempfile.TemporaryDirectory(prefix='correction-tests-') as t:
        base=Path(t)/'original'; build(archive,base,Path('.'),photos_only=True)
        good=Path(t)/'good'; r=run(base,archive,Path('.'),good,True)
        assert r['strict_links']==55 and len(r['format_mismatches'])==2
        results.append({'test':'clean original photo assembly','passed':True})
        def change_csv(path,change):
            fields,rows=csv_read(path); change(rows); path.unlink();write(path,fields,rows)
        def mutate(name,relative,change):
            cp=Path(t)/'copy';shutil.copytree(base,cp); out=Path(t)/'rejected'
            try:
                change_csv(cp/relative,change)
                try: run(cp,archive,Path('.'),out,True)
                except ValueError as e:
                    assert not out.exists();results.append({'test':name,'passed':True,'rejection':str(e).replace(str(cp),'<test-copy>')})
                else: raise AssertionError('Accepted mutation: '+name)
            finally: shutil.rmtree(cp)
        for name,key,value in [('broken link path','photo_path_from_dataset_root','photos/missing.jpg'),('RNF insertion','failure_type','RNF'),('unknown association','association_kind','UNSUPPORTED'),('training flag','training_eligible','true'),('confirmed label','verified_target','TWF'),('same-event flag','same_event_pair','true'),('path traversal','photo_path_from_dataset_root','../outside.jpg')]:
            mutate(name,'class_photo_links.csv',lambda rows,k=key,v=value:rows[0].__setitem__(k,v))
        mutate('duplicate link','class_photo_links.csv',lambda rows:rows.__setitem__(1,dict(rows[0])))
        mutate('changed rights','photo_index.csv',lambda rows:rows[0].__setitem__('reuse_rights','VERIFIED'))
        mutate('wrong class-folder link','OSF/photo_links.csv',lambda rows:rows[0].__setitem__('failure_type','TWF'))
        mutate('incorrect canonical photo path','photo_index.csv',lambda rows:rows[0].__setitem__('canonical_local_path','../outside.jpg'))
        # Real legacy view constructed from the verified output; corrupt only its derived eligibility flag.
        legacy=base/'photo_only_review';legacy.mkdir();
        for name in ('photo_index.csv','class_photo_links.csv','excluded_class_photo_links.csv'):
            shutil.copyfile(good/name,legacy/name)
        shutil.copyfile(HERE/'media_review_225.csv',legacy/'media_review_225.csv')
        for m in ('TWF','HDF','PWF','OSF','RNF'):
            (legacy/m).mkdir();shutil.copyfile(good/m/'photo_links.csv',legacy/m/'photo_links.csv')
        mutate('legacy media eligibility corruption','photo_only_review/media_review_225.csv',lambda rows:rows[0].__setitem__('strict_photo_reference_eligible','false' if rows[0]['strict_photo_reference_eligible']=='true' else 'true'))
        mutate('legacy filtered duplicate','photo_only_review/class_photo_links.csv',lambda rows:rows.__setitem__(1,dict(rows[0])))
        for case in ('modified bytes','extra file'):
            cp=Path(t)/'copy';shutil.copytree(base,cp); out=Path(t)/'rejected'
            p=next((cp/'photos').iterdir()) if case=='modified bytes' else cp/'photos/extra.jpg';p.write_bytes(b'corrupted test copy')
            try: run(cp,archive,Path('.'),out,True)
            except ValueError as e: assert not out.exists();results.append({'test':case,'passed':True,'rejection':str(e).replace(str(cp),'<test-copy>')})
            else: raise AssertionError(case)
            finally: shutil.rmtree(cp)
        try: run(base,archive,Path('.'),good,True)
        except ValueError:results.append({'test':'refuse overwrite','passed':True})
        else: raise AssertionError('overwrite')
        # No raw/index present: full audit must fail closed, not silently use legacy prepared data.
        try: run(base,archive,Path(t)/'missing-source',Path(t)/'full',False)
        except FileNotFoundError:results.append({'test':'missing original AI4I fails closed','passed':True})
        else: raise AssertionError('missing source accepted')
    return {'passed':len(results),'failed':0,'scope':'real photo-side plus missing-AI4I negative test; no full AI4I run','tests':results}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--images-zip',type=Path,required=True);a=p.parse_args();print(json.dumps(main(a.images_zip),indent=2))
