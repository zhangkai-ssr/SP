import unittest, json
from PIL import Image, ImageDraw
import render

class V2Tests(unittest.TestCase):
    def test_watch_stop_and_run(self):
        def frame(t,running):
            im=Image.new('RGB',(500,500))
            render.watch(ImageDraw.Draw(im),250,250,140,t,running)
            return im.tobytes()
        self.assertEqual(frame(3,False),frame(8,False))
        self.assertNotEqual(frame(3,True),frame(8,True))

    def test_every_shot_renders_and_is_repeatable(self):
        story=json.loads((render.ROOT/'storyboard.json').read_text(encoding='utf-8'))
        for scene in story['scenes']:
            self.assertTrue(scene['action'])
            first=render.draw_frame(scene,1,1,'测试字幕，不遮挡关键动作。')
            self.assertEqual(first.size,(1280,720))
            self.assertEqual(first.tobytes(),render.draw_frame(scene,1,1,'测试字幕，不遮挡关键动作。').tobytes())
            self.assertNotEqual(first.tobytes(),render.draw_frame(scene,5,5,'测试字幕，不遮挡关键动作。').tobytes())

    def test_audio_alignment_and_subtitle_completeness(self):
        import re
        story={'voice':'test-voice','rate':'-3%','scenes':[
            {'narration':'先记录故障，再检查结果。'},
            {'narration':'把这次排查时发现的错误原因和有效检查方法完整记录下来，下一次从这里接着走。'}]}
        aud=[{'narration':s['narration'],'voice':story['voice'],'rate':story['rate'],
              'duration':duration,'boundaries':[{'text':s['narration'],'offset':0,'duration':round(duration*10_000_000)}]}
             for s,duration in zip(story['scenes'],[3.5,8.2])]
        render.validate_audio(story,aud)
        tl=render.make_timeline([x['duration'] for x in aud])
        cues=render.subtitle_cues(story,aud,tl)
        clean=lambda s:re.sub(r'[^\w\u4e00-\u9fff]','',s)
        self.assertEqual(clean(''.join(s['narration'] for s in story['scenes'])),clean(''.join(c['text'] for c in cues)))
        self.assertTrue(all(0<=c['start']<c['end']<=tl[-1]['end'] for c in cues))
        self.assertTrue(all(len(c['text'])<=24 for c in cues))
        aud[0]['narration']='旧稿'
        with self.assertRaises(ValueError): render.validate_audio(story,aud)

if __name__=='__main__': unittest.main()
