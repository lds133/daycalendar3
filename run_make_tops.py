from settings import CFG
from draw.make_bmps import CopyTopBMPs
from draw.make_startpage import MakeReadme


cfg = CFG()
CopyTopBMPs(cfg)
MakeReadme(cfg)