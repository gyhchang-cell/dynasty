"""Isolate new art when concurrent legacy UV or elite files must be preserved."""
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
ASSETS=REPO/'src/main/resources/assets/dynasty'
ISOLATED={'fuhun_baibu_tongzi','zhiren_jianke','xianzhen_duantoujiang','qianji_bailian_yanshi','yanshi_clockwork_spider'}
def resource_paths(name):
    sub='blueprint/cod2_voxel' if name in ISOLATED else 'blueprint'
    return (ASSETS/f'geo/{sub}/{name}.geo.json',
            ASSETS/f'animations/{sub}/{name}.animation.json',
            ASSETS/f'textures/entity/{sub}/{name}.png')
