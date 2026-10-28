"""验证复利动画的内容边界、确定性与字幕安全区。"""
import unittest
import numpy as np
import render


class SnowballTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        render.load_assets()

    def test_math_is_a_model_not_a_promise(self):
        self.assertAlmostEqual(render.model_value(0), 100)
        self.assertAlmostEqual(render.model_value(1), 110)
        self.assertAlmostEqual(render.model_value(2), 121)
        self.assertAlmostEqual(render.model_value(10), 259.37424601)

    def test_new_scenes_move_and_are_deterministic(self):
        for kind in ('snow', 'reset', 'compare', 'formula', 'notebook', 'feedback', 'paths', 'bridge', 'workshop', 'final'):
            scene = {'kind': kind, 'chapter': 0, 'headline': '让昨天留下来', 'step': 1, 'narration': '测试', 'labels': ['保留', '改进', '检验']}
            a = render.draw_frame(scene, 1, 1, '每次出发，都带上昨天的经验。')
            b = render.draw_frame(scene, 2, 2, '每次出发，都带上昨天的经验。')
            self.assertEqual(a.size, (1280, 720))
            self.assertEqual(a.tobytes(), render.draw_frame(scene, 1, 1, '每次出发，都带上昨天的经验。').tobytes())
            self.assertGreater(np.mean(np.any(np.asarray(a)[170:610] != np.asarray(b)[170:610], axis=2)), .002, kind)

    def test_scene_labels_follow_the_narration(self):
        from unittest.mock import patch
        for kind in ('notebook', 'feedback', 'paths'):
            texts = ['看反馈', '看代价', '再决定'] if kind == 'feedback' else ['先看旧记录', '再补新发现']
            scene = {'kind':kind, 'chapter':0, 'headline':'测试', 'labels':texts}
            with patch.object(render, 'label', wraps=render.label) as labels:
                render.draw_frame(scene, 2, 2, '')
                drawn = [call.args[2] for call in labels.call_args_list]
            for text in texts:
                self.assertIn(text, drawn)

    def test_bridge_labels_stay_above_the_walking_character(self):
        from unittest.mock import patch
        scene = {'kind':'bridge', 'chapter':2, 'headline':'测试', 'labels':['画画的构图','视频的分镜']}
        with patch.object(render, 'label', wraps=render.label) as labels:
            render.draw_frame(scene, 7, 7, '')
            for call in labels.call_args_list:
                if call.args[2] in scene['labels']:
                    self.assertLess(call.args[1][1], 300)

    def test_timeline_and_stale_audio(self):
        tl = render.make_timeline([2.3, 3.1])
        self.assertAlmostEqual(tl[-1]['end'], 6.1)
        with self.assertRaises(ValueError):
            render.make_timeline([float('nan')])
        story = {'voice':'v', 'rate':'-3%', 'scenes':[{'narration':'新稿'}]}
        with self.assertRaises(ValueError):
            render.validate_audio(story, [{'voice':'v','rate':'-3%','narration':'旧稿'}])


if __name__ == '__main__':
    unittest.main()
