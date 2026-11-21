"""Gera ícones e logos do crieIAtive Desk a partir dos SVGs da marca.

Uso:  python crieiative/marca/gerar_marca.py   (na raiz do repo)
Precisa de Chrome (render headless) e Pillow.
"""
import base64, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
CHROME = next(p for p in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
] if os.path.exists(p))

SIMBOLO = (AQUI / "crieiative-simbolo.svg").read_text(encoding="utf-8")
FONTE = base64.b64encode((AQUI / "jost-latin-wght.woff2").read_bytes()).decode()
GRAD = "linear-gradient(0deg,#8E00A6 0%,#8E00A6 35%,#FFB950 100%)"


def render(html: str, w: int, h: int, out: Path):
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "p.html"
        f.write_text(html, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={w},{h}", "--default-background-color=00000000",
                        f"--screenshot={out}", f.as_uri()], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(out).convert("RGBA")
    if im.size != (w, h):
        im = im.crop((0, 0, w, h))
    im.save(out)


def icone(tam: int, out: Path, raio=0.22, escala=0.72):
    html = f"""<html><body style="margin:0;background:transparent">
<div style="width:{tam}px;height:{tam}px;border-radius:{int(tam*raio)}px;background:#14101A;
display:flex;align-items:center;justify-content:center">
<div style="width:{int(tam*escala)}px;height:{int(tam*escala)}px">{SIMBOLO.replace('width="512" height="512"', 'width="100%" height="100%"')}</div>
</div></body></html>"""
    render(html, tam, tam, out)


def logo(cor_texto: str, svg_logo: str, out: Path):
    logo_b64 = base64.b64encode((AQUI / svg_logo).read_bytes()).decode()
    html = f"""<html><head><style>
@font-face{{font-family:Jost;src:url(data:font/woff2;base64,{FONTE}) format('woff2');font-weight:100 900}}
body{{margin:0;background:transparent}}
.l{{display:flex;align-items:center;height:160px;padding:0 4px}}
.d{{font-family:Jost;font-weight:500;font-size:118px;line-height:1;margin-left:26px;margin-top:-6px;
background:{GRAD};-webkit-background-clip:text;background-clip:text;color:transparent}}
</style></head><body><div class="l"><img src="data:image/svg+xml;base64,{logo_b64}" style="height:130px">
<span class="d">Desk</span></div></body></html>"""
    tmp = out.with_suffix(".full.png")
    render(html, 1100, 160, tmp)
    im = Image.open(tmp)
    im.crop(im.getbbox()).save(out)
    tmp.unlink()


def main():
    build = AQUI / "build"
    build.mkdir(exist_ok=True)
    base = build / "icon-1024.png"
    icone(1024, base)
    big = Image.open(base)

    def png(tam, dest):
        dest = RAIZ / dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        big.resize((tam, tam), Image.LANCZOS).save(dest)

    # tamanhos pequenos (barra/bandeja): símbolo maior e canto menor, senão o losango some
    peq = build / "icon-small-256.png"
    icone(256, peq, raio=0.18, escala=0.9)
    small = Image.open(peq)
    frames = [(small if t <= 32 else big).resize((t, t), Image.LANCZOS)
              for t in (256, 128, 64, 48, 32, 24, 16)]
    for ico in ["res/icon.ico", "res/tray-icon.ico", "flutter/windows/runner/resources/app_icon.ico"]:
        frames[0].save(RAIZ / ico, format="ICO", sizes=[f.size for f in frames], append_images=frames[1:])
    small.resize((32, 32), Image.LANCZOS).save(RAIZ / "res/32x32.png")
    for tam, dest in [(64, "res/64x64.png"), (128, "res/128x128.png"),
                      (256, "res/128x128@2x.png"), (512, "res/icon.png"), (1024, "res/mac-icon.png"),
                      (512, "flutter/assets/icon.png")]:
        png(tam, dest)

    # ícone SVG (fallback da interface): o próprio símbolo
    shutil.copy(AQUI / "crieiative-simbolo.svg", RAIZ / "flutter/assets/icon.svg")

    logo("#14101A", "crieiative-logo.svg", RAIZ / "flutter/assets/logo_light.png")
    logo("#FFFFFF", "crieiative-logo-dark.svg", RAIZ / "flutter/assets/logo_dark.png")
    print("marca gerada")


if __name__ == "__main__":
    sys.exit(main())
