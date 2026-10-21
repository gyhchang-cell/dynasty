"""Regression checks for export false alarms, including genuine failure cases."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image
from verify_ftbquests import advancement_ids
from verify_gear import texture_errors
from verify_lang import CUSTOM_RENDER_MODELS, custom_model_errors


class ExportVerifierTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.texture = self.root / 'charm.png'
        self.model = self.root / 'charm.json'
        Image.new('RGBA', (37, 45), (20, 40, 60, 255)).save(self.texture)
        self.model.write_text(json.dumps({'loader': 'dynasty:original_item',
                                         'original_texture': 'dynasty:textures/item/charm.png'}))
        self.approved = {'charm': {'size': [37, 45],
                                  'sha256': hashlib.sha256(self.texture.read_bytes()).hexdigest()}}

    def test_nested_advancements_keep_namespace_and_path(self):
        ids = advancement_ids(['data/dynasty/advancements/dungeons/defeat_chensha_jinwu.json',
                               'data/other/advancements/defeat_chensha_jinwu.json',
                               'assets/dynasty/models/item/charm.json'])
        self.assertEqual({'dynasty:dungeons/defeat_chensha_jinwu',
                          'other:defeat_chensha_jinwu'}, ids)
        self.assertNotIn('dynasty:defeat_chensha_jinwu', ids)
        self.assertNotIn('other:dungeons/defeat_chensha_jinwu', ids)

    def errors(self, approved=None):
        return texture_errors('charm', self.texture, self.model, 32,
                              self.approved if approved is None else approved)

    def test_approved_non_square_original_is_accepted(self):
        self.assertEqual([], self.errors())

    def test_unapproved_high_resolution_is_still_rejected(self):
        self.assertTrue(self.errors({}))

    def test_changed_pixels_are_rejected_at_identical_size(self):
        Image.new('RGBA', (37, 45), (255, 0, 0, 255)).save(self.texture)
        self.assertTrue(self.errors())

    def test_wrong_loader_is_rejected(self):
        self.model.write_text('{"parent":"minecraft:item/generated"}')
        self.assertTrue(self.errors())

    def test_fully_transparent_original_is_rejected_even_with_matching_hash(self):
        Image.new('RGBA', (37, 45), (0, 0, 0, 0)).save(self.texture)
        self.approved['charm']['sha256'] = hashlib.sha256(self.texture.read_bytes()).hexdigest()
        self.assertTrue(self.errors())

    def test_only_explicit_render_models_are_exempt(self):
        self.assertNotIn('unregistered_icon', CUSTOM_RENDER_MODELS)
        for variant, base in CUSTOM_RENDER_MODELS.items():
            (self.root / (base + '.json')).write_text('{"parent":"builtin/entity"}')
            self.assertEqual([], custom_model_errors(variant, {base, variant}, self.root))
            self.assertTrue(custom_model_errors(variant, {variant}, self.root))

    def test_custom_model_requires_custom_rendering_base(self):
        base = CUSTOM_RENDER_MODELS['taiyi_whisk_icon']
        (self.root / (base + '.json')).write_text('{"parent":"minecraft:item/generated"}')
        self.assertTrue(custom_model_errors('taiyi_whisk_icon', {base}, self.root))


if __name__ == '__main__':
    unittest.main()
