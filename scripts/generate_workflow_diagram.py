import argparse
import struct
import textwrap
import zlib

W, H = 2600, 1600
bg = (245, 248, 252)
img = [[list(bg) for _ in range(W)] for _ in range(H)]

# 5x7 bitmap font
FONT = {
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10011','10001','10001','01110'],
'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'J':['00001','00001','00001','00001','10001','10001','01110'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'Q':['01110','10001','10001','10001','10101','10010','01101'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],
'W':['10001','10001','10001','10101','10101','10101','01010'],
'X':['10001','10001','01010','00100','01010','10001','10001'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],
'Z':['11111','00001','00010','00100','01000','10000','11111'],
'0':['01110','10001','10011','10101','11001','10001','01110'],
'1':['00100','01100','00100','00100','00100','00100','01110'],
'2':['01110','10001','00001','00010','00100','01000','11111'],
'3':['11110','00001','00001','01110','00001','00001','11110'],
'4':['00010','00110','01010','10010','11111','00010','00010'],
'5':['11111','10000','10000','11110','00001','00001','11110'],
'6':['01110','10000','10000','11110','10001','10001','01110'],
'7':['11111','00001','00010','00100','01000','01000','01000'],
'8':['01110','10001','10001','01110','10001','10001','01110'],
'9':['01110','10001','10001','01111','00001','00001','01110'],
'-':['00000','00000','00000','11111','00000','00000','00000'],
'/':['00001','00010','00100','01000','10000','00000','00000'],
'&':['01100','10010','10100','01000','10101','10010','01101'],
'+':['00000','00100','00100','11111','00100','00100','00000'],
' ':['00000','00000','00000','00000','00000','00000','00000'],
':':['00000','00100','00100','00000','00100','00100','00000'],
'.':['00000','00000','00000','00000','00000','00110','00110'],
'(':[ '00010','00100','01000','01000','01000','00100','00010'],
')':[ '01000','00100','00010','00010','00010','00100','01000'],
}

def setpx(x,y,c):
    if 0 <= x < W and 0 <= y < H:
        img[y][x] = [*c]

def rect(x,y,w,h,c):
    for yy in range(y,y+h):
        if yy<0 or yy>=H: continue
        row=img[yy]
        for xx in range(x,x+w):
            if 0<=xx<W: row[xx]=[*c]

def rounded_rect(x,y,w,h,r,fill,border=None,bw=2):
    rect(x+r,y,w-2*r,h,fill); rect(x,y+r,r,h-2*r,fill); rect(x+w-r,y+r,r,h-2*r,fill)
    for yy in range(h):
        for xx in range(w):
            dx=min(xx,w-1-xx); dy=min(yy,h-1-yy)
            if dx<r and dy<r:
                cx = r-1 if xx<r else w-r
                cy = r-1 if yy<r else h-r
                if (xx-cx)**2 + (yy-cy)**2 > (r-1)**2: continue
            setpx(x+xx,y+yy,fill)
    if border:
        # naive border
        for i in range(bw):
            for xx in range(x+r,x+w-r):
                setpx(xx,y+i,border); setpx(xx,y+h-1-i,border)
            for yy in range(y+r,y+h-r):
                setpx(x+i,yy,border); setpx(x+w-1-i,yy,border)

def line(x1,y1,x2,y2,c,t=3):
    dx=abs(x2-x1); sx=1 if x1<x2 else -1
    dy=-abs(y2-y1); sy=1 if y1<y2 else -1
    err=dx+dy
    while True:
        rect(x1-t//2,y1-t//2,t,t,c)
        if x1==x2 and y1==y2: break
        e2=2*err
        if e2>=dy: err+=dy; x1+=sx
        if e2<=dx: err+=dx; y1+=sy

def arrow(x1,y1,x2,y2,c):
    line(x1,y1,x2,y2,c,4)
    if abs(x2-x1) > abs(y2-y1):
        s=-1 if x2<x1 else 1
        line(x2,y2,x2-18*s,y2-8,c,4); line(x2,y2,x2-18*s,y2+8,c,4)
    else:
        s=-1 if y2<y1 else 1
        line(x2,y2,x2-8,y2-18*s,c,4); line(x2,y2,x2+8,y2-18*s,c,4)

def draw_char(ch,x,y,scale,c):
    pat=FONT.get(ch.upper(), FONT[' '])
    for r,row in enumerate(pat):
        for col,v in enumerate(row):
            if v=='1': rect(x+col*scale,y+r*scale,scale,scale,c)

def text(s,x,y,scale=3,c=(30,41,59),maxw=None,lh=10):
    if maxw:
        chars_per=max(1,maxw//(6*scale))
        lines=textwrap.wrap(s,width=chars_per)
    else:
        lines=[s]
    for i,ln in enumerate(lines):
        for j,ch in enumerate(ln):
            draw_char(ch,x+j*6*scale,y+i*lh*scale,scale,c)

# Header
rounded_rect(40,30,W-80,130,24,(19,30,51),None)
text('AWS DATA ENGINEERING WORKFLOW',120,72,scale=5,c=(255,255,255))
text('REPOSITORY SERVICE FLOW - ALL AWS SERVICES USED',120,122,scale=2,c=(191,219,254))

nodes = [
 (100,240,280,150,'IAM IDENTITY CENTER / SSO',(255,153,0)),
 (470,240,220,150,'STS',(255,153,0)),
 (780,240,220,150,'S3',(255,153,0)),
 (1090,240,260,150,'GLUE CRAWLER + DATA CATALOG',(255,153,0)),
 (1440,240,220,150,'ATHENA',(255,153,0)),
 (1750,240,220,150,'REDSHIFT',(255,153,0)),

 (120,520,220,150,'EC2',(255,153,0)),
 (410,520,220,150,'EBS',(255,153,0)),
 (700,520,260,150,'CLOUDWATCH',(255,153,0)),
 (1030,520,220,150,'SNS',(255,153,0)),
 (1320,520,300,150,'CLOUDFORMATION',(255,153,0)),

 (260,810,280,150,'RDS MYSQL',(255,153,0)),
 (620,810,280,150,'AURORA',(255,153,0)),
 (980,810,280,150,'DYNAMODB',(255,153,0)),
 (1340,810,250,150,'LAMBDA',(255,153,0)),
 (1670,810,300,150,'STEP FUNCTIONS',(255,153,0)),
]

for x,y,w,h,label,ic in nodes:
    rounded_rect(x,y,w,h,18,(255,255,255),(203,213,225),3)
    rounded_rect(x+14,y+18,56,56,12,ic)
    text('AWS',x+22,y+38,scale=2,c=(255,255,255))
    text(label,x+84,y+42,scale=2,c=(15,23,42),maxw=w-100,lh=8)

# arrows top row
for i in range(5):
    x1,y1,w1,h1,*_=nodes[i]
    x2,y2,w2,h2,*_=nodes[i+1]
    arrow(x1+w1,y1+h1//2,x2,y2+h2//2,(59,130,246))
# branching from S3/athena/ec2
arrow(890,390,230,520,(59,130,246))   # s3->ec2
arrow(1550,390,440,810,(59,130,246))  # athena->rds
arrow(1550,390,760,810,(59,130,246))  # athena->aurora
arrow(1550,390,1120,810,(59,130,246)) # athena->dynamo
# ec2 chain
arrow(340,595,410,595,(59,130,246))
arrow(630,595,700,595,(59,130,246))
arrow(960,595,1030,595,(59,130,246))
arrow(1250,595,1320,595,(59,130,246))
# orchestration
arrow(1260,885,1340,885,(59,130,246))
arrow(1590,885,1670,885,(59,130,246))
arrow(1860,390,1465,810,(59,130,246))

text('DATA QUALITY ORCHESTRATION',1460,1020,scale=2,c=(30,64,175))
text('STEP FUNCTIONS -> LAMBDA -> ATHENA/REDSHIFT CHECKS',1340,1060,scale=2,c=(71,85,105))
text('SOURCE: README + DOCS SERVICE SUMMARY',80,1520,scale=2,c=(100,116,139))

# Write PNG

def chunk(tag,data):
    return struct.pack('!I',len(data))+tag+data+struct.pack('!I',zlib.crc32(tag+data)&0xffffffff)

raw=b''
for row in img:
    raw += b'\x00' + bytes([v for px in row for v in px])

png = b'\x89PNG\r\n\x1a\n'
png += chunk(b'IHDR', struct.pack('!IIBBBBB',W,H,8,2,0,0,0))
png += chunk(b'IDAT', zlib.compress(raw,9))
png += chunk(b'IEND', b'')

parser = argparse.ArgumentParser(description='Generate AWS services workflow PNG')
parser.add_argument(
    '--output',
    default='evidence/aws_workflow_all_services.png',
    help='Output PNG path (default: evidence/aws_workflow_all_services.png)'
)
args = parser.parse_args()

with open(args.output, 'wb') as f:
    f.write(png)
print(f'created {args.output}')
