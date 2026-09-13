from settings import CFG
from draw.make_bmps import MakeBottomBMPs
from draw.make_startpage import MakeReadmeBMP



cfg = CFG()
MakeBottomBMPs(cfg)
MakeReadmeBMP(cfg)