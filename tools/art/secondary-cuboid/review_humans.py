"""Current five human models, actual UV/PNG, same-scale SOFTWARE diagnosis."""
import review_materials as review
from human_atlas import IDS
from build_models import REPO

review.IDS=IDS
review.OUT=REPO/'docs/art/secondary-humans-v3'
review.BEFORE=REPO/'build/maintenance/secondary-humans-v3/before'
review.GRAY=REPO/'build/maintenance/secondary-humans-v3/gray.png'
review.TITLE='Five ordinary people / actual PNG + UV / same scale / SOFTWARE ONLY'

if __name__=='__main__':review.main()
