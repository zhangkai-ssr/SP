# 本片像素资产

- `workshop.png`：AI生成的工坊背景。
- `character_sheet.png`：带透明度的4×2角色姿势表；从左到右、从上到下为站立、步态A、步态B、思考、读书、指向、修表、休息。
- `provenance.json`：两张图的完整提示词、工具、日期与SHA-256。
- `douyin_avatar.png`、`douyin_cover.png`：沿用本片角色和蓝金配色的方形账号头像、竖版视频封面。
- `douyin_provenance.json`：头像和封面的内置imagegen提示词、尺寸、日期与SHA-256。
- `douyin_cover.png`为当前采用的竖版封面；用户实测截图反馈后，此系列后续默认竖屏。
- `douyin_cover_landscape.png`：制作过程中重新排版的16:9横版封面，保留作参考；生成记录见`douyin_landscape_provenance.json`。

渲染按等分单元格读取角色，再按透明度范围裁边、等比缩放作图层合成；原图保留。画面的图形道具和动态由本项目脚本生成。参考作者的视频和美术不在本目录。
