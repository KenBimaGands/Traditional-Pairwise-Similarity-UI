"""Render saved sample results; no extraction or baseline writes."""
import csv
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from revised_pipeline import ROOT, HERE, region, read_csv, write_csv
from extract_features import Config, load_image


def layout_overlay(rgb, vector):
    image = Image.fromarray(rgb).convert('RGBA')
    overlay = Image.new('RGBA', image.size)
    draw = ImageDraw.Draw(overlay)
    height,width=rgb.shape[:2]
    xs,ys=np.linspace(0,width,5,dtype=int),np.linspace(0,height,9,dtype=int)
    for j in range(8):
        for i in range(4):
            value=float(vector[j*4+i])
            draw.rectangle((int(xs[i]),int(ys[j]),int(xs[i+1]-1),int(ys[j+1]-1)),fill=(255,0,0,round(160*value)),outline=(0,200,200,160))
    return Image.alpha_composite(image,overlay).convert('RGB')


def main():
    run=HERE/'sample_run_02'
    manifest=json.loads((run/'roi_manifest.json').read_text())
    metadata={r['screen_id']:r for r in read_csv(ROOT/'PILOT/screenshots/screens.csv','utf-8-sig')}
    baseline={r['screen_id']:r for r in read_csv(ROOT/'results/layout_vectors.csv')}
    layouts={name:{r['screen_id']:r for r in read_csv(run/name/'layout_vectors.csv')} for name in ['row_background','local_median']}
    (run/'layout_edge_comparisons').mkdir(exist_ok=True)
    pages=[Image.new('RGB',(1000,4*490),'white') for _ in range(3)]
    for index,(sid,record) in enumerate(manifest.items()):
        rgb,_=load_image(ROOT/'PILOT/screenshots'/metadata[sid]['image_path'],Config())
        roi=rgb[:record['bounds_xyxy'][3]]
        base_gray=cv2.GaussianBlur(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),(5,5),1)
        roi_gray=cv2.GaussianBlur(cv2.cvtColor(roi,cv2.COLOR_RGB2GRAY),(5,5),1)
        base_edge=Image.fromarray(cv2.Canny(base_gray,50,150)).convert('RGB')
        roi_edge=Image.fromarray(cv2.Canny(roi_gray,50,150)).convert('RGB')
        base_plot=read_csv(ROOT/'visual_quality_review/selected_screens.csv')[index]['existing_plot']
        diagnostic=Image.open(ROOT/base_plot)
        w,h=diagnostic.size
        mask_panel=diagnostic.crop((2*w//3,38,w,h//2-8))
        masks=[Image.open(run/method/'masks'/f'{sid}.png').convert('RGB') for method in ['row_background','local_median']]
        page=pages[index//4]; draw=ImageDraw.Draw(page); y=(index%4)*490
        draw.text((5,y+5),sid,fill='black')
        for col,(name,image) in enumerate(zip(['ROI image','Saved baseline mask','Row model mask','Local median mask'],[Image.fromarray(roi),mask_panel,*masks])):
            draw.text((col*250+5,y+25),name,fill='black')
            image.thumbnail((242,438),Image.Resampling.LANCZOS)
            page.paste(image,(col*250+(250-image.width)//2,y+48))
        panels=[('Original',Image.fromarray(rgb)),('Baseline Canny',base_edge),('ROI Canny',roi_edge),('Baseline layout',layout_overlay(rgb,[baseline[sid][f'cell_{i:02d}'] for i in range(32)]))]
        for method in ['row_background','local_median']:
            panels.append((method+' layout',layout_overlay(roi,[layouts[method][sid][f'cell_{i:02d}'] for i in range(32)])))
        canvas=Image.new('RGB',(1440,590),'white'); draw=ImageDraw.Draw(canvas); draw.text((5,5),sid+' | layout: red opacity = union occupancy; cyan = grid',fill='black')
        for col,(name,image) in enumerate(panels):
            draw.text((col*240+5,30),name,fill='black'); image.thumbnail((232,510),Image.Resampling.LANCZOS); canvas.paste(image,(col*240+(240-image.width)//2,60))
        canvas.save(run/'layout_edge_comparisons'/f'{sid}.png')
    deltas=[]
    for method, screens in layouts.items():
        for sid,row in screens.items():
            deltas.append(dict(screen_id=sid, method=method, **{f'cell_{i:02d}_delta':float(row[f'cell_{i:02d}'])-float(baseline[sid][f'cell_{i:02d}']) for i in range(32)}))
    write_csv(run/'layout_differences.csv',deltas)
    for i,page in enumerate(pages):
        page.save(run/f'mask_contact_sheet_{i+1}.png')


if __name__=='__main__':
    main()
