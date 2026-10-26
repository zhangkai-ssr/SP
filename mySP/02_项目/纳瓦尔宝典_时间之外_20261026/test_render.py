"""只验证本项目的时间线和动画输出。"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


class RenderTests(unittest.TestCase):
    def test_render_rejects_stale_audio(self):
        import render
        self.assertTrue(hasattr(render, 'validate_audio'), '渲染前必须核对旁白与分镜')
        story = {'voice': 'voice-a', 'rate': '-3%', 'scenes': [{'narration': '第一句'}]}
        audio = [{'narration': '第一句', 'voice': 'voice-a', 'rate': '-3%'}]
        render.validate_audio(story, audio)
        for key, value in [('narration', '新文案'), ('voice', 'voice-b'), ('rate', '+0%')]:
            with self.assertRaises(ValueError):
                render.validate_audio(story, [{**audio[0], key: value}])

    def test_audio_cache_changes_with_input(self):
        import prepare_audio
        self.assertTrue(hasattr(prepare_audio, 'cache_name'), '旁白缓存必须区分文案和声音设置')
        original = prepare_audio.cache_name(0, '第一句', 'voice-a', '-3%')
        for args in [('另一句', 'voice-a', '-3%'), ('第一句', 'voice-b', '-3%'), ('第一句', 'voice-a', '+0%')]:
            self.assertNotEqual(original, prepare_audio.cache_name(0, *args))

    def test_service_sentence_overlap_is_clipped(self):
        import render
        story = {'scenes': [{'narration': '第一句。第二句。'}]}
        audio = [{'boundaries': [
            {'text': '第一句。', 'offset': 1000000, 'duration': 10000000},
            {'text': '第二句。', 'offset': 10500000, 'duration': 10000000}
        ]}]
        cues = render.subtitle_cues(story, audio, render.make_timeline([2.2]))
        self.assertLessEqual(cues[0]['end'], cues[1]['start'])

    def test_timeline_and_animation(self):
        self.assertTrue((ROOT / 'render.py').exists(), '缺少可运行的动画渲染入口')
        spec = importlib.util.spec_from_file_location('naval_render', ROOT / 'render.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        timeline = renderer.make_timeline([2.3, 3.1])
        self.assertEqual(timeline[0]['start'], 0)
        self.assertAlmostEqual(timeline[-1]['end'], 6.1)
        self.assertEqual(timeline[0]['end'], timeline[1]['start'])
        with self.assertRaises(ValueError):
            renderer.make_timeline([0, -1])
        renderer.load_assets()
        scene = {'chapter': 0, 'kind': 'clock', 'headline': '测试时间', 'narration': '测试'}
        a = renderer.draw_frame(scene, 0.1, 0.1, '测试字幕')
        b = renderer.draw_frame(scene, 1.1, 1.1, '测试字幕')
        self.assertEqual(a.size, (1280, 720))
        self.assertNotEqual(a.tobytes(), b.tobytes())


if __name__ == '__main__':
    unittest.main()
