"""Download original H2O Text2HOI inference weights from the upstream public folder.

Usage: python scripts/download_checkpoints.py --output checkpoints/h2o
Install gdown first: python -m pip install '.[download]'
"""
import argparse
import hashlib
import json
from pathlib import Path

FILES = {"contact_estimator": "18xUQgxntYA0RB0eqdXc0omqbSSUEUD3c",
         "pointfeat": "1UPIW0Z0VunNZSbO994EmbC17eRPyQdX5",
         "texthom": "1aLNSFOe1wuZA4nKzhlsvL6hOMxHm06ew"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("checkpoints/h2o"))
    args=parser.parse_args()
    try:
        import gdown
    except ImportError:
        parser.exit(2,"Install downloader: python -m pip install '.[download]'\n")
    args.output.mkdir(parents=True,exist_ok=True)
    manifest={}
    for name,fid in FILES.items():
        path=args.output/f"{name}.pth"
        if not path.is_file():
            temporary=path.with_suffix(".download")
            result=gdown.download(id=fid,output=str(temporary),quiet=False)
            if result is None or not temporary.exists():
                parser.exit(2,f"Download failed: {name}. See docs/text2hoi.md for manual downloads.\n")
            temporary.replace(path)
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''): digest.update(chunk)
        manifest[name]={"google_drive_id":fid,"sha256":digest.hexdigest(),"bytes":path.stat().st_size}
    (args.output/'downloads.json').write_text(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    main()
