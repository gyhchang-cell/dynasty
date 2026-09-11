"""王朝生物贴图：12 个人形 + 3 只神兽（严格对齐模型 UV）。"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(__file__))
from artlib import Cv, hx, mix, lighten, darken, ramp
from palette import *
from entity_kit import box, face, humanoid_skin, INK

OUT = os.path.join(os.path.dirname(__file__), "out/entity")

SKIN_N = ramp(hx("D9A57A"), 5)
TERRACOTTA = ramp(hx("B4783C"), 5)
FUR_RED = ramp(hx("C0392B"), 5)
IRON = ramp(hx("5A6472"), 5)
PURPLE = ramp(hx("6B3E8F"), 5)
BLUE_ROBE = ramp(hx("2E4A8B"), 5)
GREEN_ROBE = ramp(hx("4E7A4A"), 5)


def humanoids():
    humanoid_skin("terracotta_warrior", TERRACOTTA, TERRACOTTA, ramp(hx("7A4A1E"), 5),
                  "topknot", armor=True, lamellae=True, hair=ramp(hx("6B3A14"), 5))
    humanoid_skin("imperial_soldier", SKIN_N, RED_LACQUER, GOLD, "helmet", armor=True,
                  hair=ramp(hx("2A1A14"), 5))
    humanoid_skin("undead_first_emperor", SKIN_JADE, ramp(hx("3A2A5A"), 5), GOLD, "crown",
                  armor=True, eye=(190, 240, 200, 255), hair=ramp(hx("2A1A3A"), 5))
    humanoid_skin("minister", SKIN_N, BLUE_ROBE, ramp(hx("E8DCC0"), 5), "mustache",
                  hair=ramp(hx("3A3A3A"), 5))
    humanoid_skin("assassin", SKIN_ASH, BLACK_CLOTH, ramp(hx("8B1F1F"), 5), "mask",
                  hair=ramp(hx("1A1A22"), 5), eye=(200, 60, 60, 255))
    humanoid_skin("archer", SKIN_N, GREEN_ROBE, LEATHER, "helmet",
                  hair=ramp(hx("3A2A14"), 5))
    humanoid_skin("royal_guard", SKIN_N, RED_SILK, GOLD, "honor_guard", armor=True,
                  hair=ramp(hx("1A1414"), 5))
    humanoid_skin("rebel_soldier", SKIN_N, LEATHER, ramp(hx("6B4A2A"), 5), "hood",
                  hair=ramp(hx("3A2A1A"), 5))
    humanoid_skin("nian_beast", FUR_RED, ramp(hx("8B1A14"), 5), GOLD, "beard",
                  hair=ramp(hx("5A1410"), 5), eye=(255, 220, 120, 255))
    humanoid_skin("dragon_emperor", SKIN_N, ramp(hx("A82C1E"), 5), GOLD, "crown",
                  armor=True, hair=ramp(hx("1A1414"), 5))
    humanoid_skin("rebel_general", SKIN_N, IRON, GOLD, "helmet", armor=True,
                  hair=ramp(hx("2A1A1A"), 5))
    humanoid_skin("eunuch_mastermind", ramp(hx("E0C0A0"), 5), PURPLE, GOLD, "hood",
                  hair=ramp(hx("2A1A2A"), 5), eye=(120, 60, 140, 255))
    print("humanoids done:", len(os.listdir(OUT)))


if __name__ == "__main__":
    humanoids()
