from core.config_manager import config

TRANSLATIONS = {
    "zh": {
        "Settings": "✨ 桌面管理配置中心",
        "Home": "🏠 核心使用说明",
        "Appearance": "🎨 外观与排版",
        "BoxRules": "📦 盒子与规则",
        "DesktopHook": "⚡ 原生桌面接管",
        "SystemAdv": "⚙️ 系统高级配置",
        
        "GuideTitle": "<h1 style='font-size:24px; font-weight:normal;'>桌面增强管理器 - 核心指南</h1>",
        "GuideText": """
        <p style='line-height: 1.8;'>
        <b>✨ 基础操作指南：</b><br>
        • <b>智能映射：</b>将任意文件直接拖入【主盒子】，程序将根据您设定的后缀规则，自动将其分配至对应标签页。<br>
        • <b>虚拟重命名：</b>在盒子内右键文件图标，可以对其进行重命名，仅在盒子内生效，绝不修改您的真实文件！<br>
        • <b>自由收纳：</b>您可以在配置中心新建无限个【独立盒子】。将鼠标移至盒子边缘，可自由拉伸调整尺寸。<br>
        • <b>多标签页：</b>独立盒子同样支持标签页！在配置中心的“盒子管理”中点击 [🏷️标签管理] 即可自由增减。<br>
        <br>
        <b>⚡ 高级交互技巧：</b><br>
        • <b>网格吸附：</b>在盒子内部按住鼠标左键随意拖动图标，松开后图标将自动吸附并对齐隐形网格。<br>
        • <b>悬浮抽屉：</b>点击盒子右上角的 <code>▶</code> 可将其折叠。当鼠标悬浮于折叠状态的盒子时，它将如抽屉般自动滑出。<br>
        • <b>弹簧锁定：</b>右键点击盒子左上角的彩色圆圈，选择【🔒 锁定】。圆圈将带有物理弹簧动画跃至前方，防止误拖动。<br>
        • <b>双击隐身：</b>在桌面任意空白处【快速双击左键】，一瞬间隐藏所有的盒子与系统桌面图标，保护隐私。
        </p>
        """,
        "LicenseTitle": "<b>📜 开源许可声明：</b>",
        "LicenseText": "<span style='color:#888;'>本项目基于 MIT License 开源。<br>允许商业使用、修改和分发，但需保留原作者版权声明。<br>底层桌面图层注入及特效原理借鉴了开源社区思想，特此致谢。</span>",
        
        "ThemeMode": "配置中心黑/白模式:",
        "GlobalColor": "配置中心全局多彩底色:",
        "BoxMaterial": "所有盒子的底层材质:",
        "BoxColor": "所有盒子的统一底色:",
        "BoxOpacity": "所有盒子的不透明度 (0-255):",
        "TabPosition": "盒子内标签栏的位置:",
        
        "BoxList": "<b>独立控制每一个盒子:</b>",
        "NewBox": "新建空白盒子",
        "Clear": "清空内容",
        "Rename": "重命名",
        "Disband": "解散",
        "TabManage": "🏷️ 标签管理",
        "Hidden": "已隐藏",
        "Shown": "已显示",
        
        "RuleTitle": "<b>主盒子文件分类规则: (支持 '__dir__' 识别文件夹)</b>",
        "AddRule": "添加新分类",
        "ApplyRule": "应用并强制刷新主盒子",
        "CatName": "分类名称",
        "ExtName": "后缀，文件夹填 __dir__",
        "Del": "删除",
        
        "HookTitle": "【安全映射引擎】：自动扫描桌面文件映射到主盒子，同时隐藏底层系统桌面。\n系统回收站等图标不会消失，且你在桌面下载新建的文件会自动抓入。",
        "ExcludeSys": "整理桌面时，自动排除 [此电脑]、[控制面板] 等系统级原生图标",
        "ExcludeExt": "整理桌面时，主动屏蔽的后缀:",
        "OrgBtn": "🚀 一键接管/整理现有桌面",
        "RestoreBtn": "↩️ 停止接管：清空主盒子记录并恢复系统桌面",
        
        "OpenMode": "图标打开触发方式:",
        "HookEnable": "启用全局鼠标监听：双击桌面任意空白处隐藏/显示系统",
        "HoverExpand": "智能抽屉：鼠标悬浮到处于[折叠]状态的盒子时自动展开",
        "HoverTab": "无触切换：在盒子内，鼠标悬浮不同标签页时自动切换 (无需点击)",
        "DataPath": "数据存放目录:",
        "ChangePath": "更改目录",
        "Reset": "恢复系统默认设置 (出厂状态)",
        "ExitApp": "🚪 彻底退出软件",
        
        # 菜单补全翻译
        "SortName": "名称", "SortSize": "大小", "SortType": "项目类型", "SortDate": "修改日期",
        "ViewLargeX": "超大图标", "ViewLarge": "大图标", "ViewMedium": "中等图标", "ViewSmall": "小图标",
        "MenuSort": "排序方式   >", "MenuView": "查看   >", "MenuOrg": "🚀 一键接管/整理桌面", "MenuRestore": "↩️ 停止接管还原桌面",
        
        "Lock": "🔒 锁定盒子", "Unlock": "🔓 解锁盒子",
        "ChangeColor": "🎨 修改盒子底色", "OpenSettings": "⚙️ 打开配置中心",
        "System": "跟随系统", "Light": "浅色模式", "Dark": "深色模式",
        "Normal": "正常纯色", "Transparent": "透明背景", "Blur": "高斯模糊", "Acrylic": "Win11 亚克力",
        "Top": "顶部", "Bottom": "底部", "Left": "左侧", "Right": "右侧"
    },
    "en": {
        "Settings": "✨ Desktop Settings",
        "Home": "🏠 Core Guide",
        "Appearance": "🎨 Appearance",
        "BoxRules": "📦 Boxes & Rules",
        "DesktopHook": "⚡ Desktop Engine",
        "SystemAdv": "⚙️ System Config",
        "GuideTitle": "<h1 style='font-size:24px; font-weight:normal;'>Desktop Organizer - Guide</h1>",
        "GuideText": "<p>Basic Operations...</p>",
        "LicenseTitle": "<b>📜 Open Source License:</b>",
        "LicenseText": "<span style='color:#888;'>Licensed under MIT License.<br>Commercial use, modification, and distribution are permitted, provided the original copyright notice is retained.<br>Thanks to the open-source community for desktop hook inspirations.</span>",
        "ThemeMode": "Panel Dark/Light Mode:",
        "GlobalColor": "Panel Accent Color:",
        "BoxMaterial": "Base Material for Boxes:",
        "BoxColor": "Global Base Color for Boxes:",
        "BoxOpacity": "Box Opacity (0-255):",
        "TabPosition": "Tab Bar Position in Boxes:",
        "BoxList": "<b>Control Individual Boxes:</b>",
        "NewBox": "New Blank Box",
        "Clear": "Clear",
        "Rename": "Rename",
        "Disband": "Disband",
        "TabManage": "🏷️ Manage Tabs",
        "Hidden": "Hidden",
        "Shown": "Shown",
        "RuleTitle": "<b>Main Box Rules: (Use '__dir__' for folders)</b>",
        "AddRule": "Add Category",
        "ApplyRule": "Apply & Refresh Main Box",
        "CatName": "Category",
        "ExtName": "Extensions (e.g., .png)",
        "Del": "Del",
        "HookTitle": "[Safe Engine]: Auto-scans desktop files into Main Box & hides native desktop.\nSystem icons (Recycle Bin) won't disappear. New downloads will be captured auto.",
        "ExcludeSys": "Exclude System Icons (This PC, Control Panel) when organizing",
        "ExcludeExt": "Extensions to Ignore:",
        "OrgBtn": "🚀 1-Click Takeover & Organize Desktop",
        "RestoreBtn": "↩️ Stop Takeover: Clear Box & Restore Desktop",
        "OpenMode": "Icon Open Mode:",
        "HookEnable": "Global Mouse Hook: Double-click desktop to hide/show",
        "HoverExpand": "Smart Drawer: Auto-expand folded boxes on hover",
        "HoverTab": "Touchless Switch: Auto-switch tabs on hover inside boxes",
        "DataPath": "Data Storage Path:",
        "ChangePath": "Change Path",
        "Reset": "Restore Factory Default Settings",
        "ExitApp": "🚪 Exit Application",
        
        "SortName": "Name", "SortSize": "Size", "SortType": "Type", "SortDate": "Date",
        "ViewLargeX": "Extra Large", "ViewLarge": "Large", "ViewMedium": "Medium", "ViewSmall": "Small",
        "MenuSort": "Sort by   >", "MenuView": "View   >", "MenuOrg": "🚀 Takeover Desktop", "MenuRestore": "↩️ Restore Desktop",
        
        "Lock": "🔒 Lock Box", "Unlock": "🔓 Unlock Box",
        "ChangeColor": "🎨 Change Color", "OpenSettings": "⚙️ Open Settings",
        "System": "System", "Light": "Light", "Dark": "Dark",
        "Normal": "Normal Color", "Transparent": "Transparent", "Blur": "Gaussian Blur", "Acrylic": "Win11 Acrylic",
        "Top": "Top", "Bottom": "Bottom", "Left": "Left", "Right": "Right"
    },
    "ja": {
        "Settings": "✨ デスクトップ管理設定",
        "Home": "🏠 使い方ガイド",
        "Appearance": "🎨 外観とテーマ",
        "BoxRules": "📦 ボックスとルール",
        "DesktopHook": "⚡ デスクトップ管理",
        "SystemAdv": "⚙️ 高級設定",
        "GuideTitle": "<h1 style='font-size:24px; font-weight:normal;'>デスクトップ拡張マネージャー - ガイド</h1>",
        "GuideText": "<p>ガイド...</p>",
        "LicenseTitle": "<b>📜 オープンソースライセンス：</b>",
        "LicenseText": "<span style='color:#888;'>このプロジェクトは MIT License のもとでオープンソース化されています。</span>",
        "ThemeMode": "設定パネルのテーマ:",
        "GlobalColor": "全体的なアクセントカラー:",
        "BoxMaterial": "ボックスの背景素材:",
        "BoxColor": "ボックスの基本色:",
        "BoxOpacity": "不透明度 (0-255):",
        "TabPosition": "タブの配置場所:",
        "BoxList": "<b>個別のボックス管理:</b>",
        "NewBox": "新しいボックス",
        "Clear": "クリア",
        "Rename": "名前変更",
        "Disband": "解散",
        "TabManage": "🏷️ タブ管理",
        "Hidden": "非表示",
        "Shown": "表示中",
        "RuleTitle": "<b>メインボックスの分類ルール: (フォルダは '__dir__')</b>",
        "AddRule": "カテゴリ追加",
        "ApplyRule": "適用して再読み込み",
        "CatName": "カテゴリ名",
        "ExtName": "拡張子 (.png など)",
        "Del": "削除",
        "HookTitle": "【安全なマッピング】：デスクトップのファイルをスキャンし、元のデスクトップを非表示にします。",
        "ExcludeSys": "整理時にシステムアイコン(PC, コントロールパネルなど)を除外する",
        "ExcludeExt": "除外する拡張子:",
        "OrgBtn": "🚀 ワンクリックでデスクトップを整理",
        "RestoreBtn": "↩️ 整理を停止：ボックスを空にして元に戻す",
        "OpenMode": "開き方:",
        "HookEnable": "ダブルクリックでデスクトップを隠す/表示する",
        "HoverExpand": "スマートドロワー：ホバーで自動展開",
        "HoverTab": "タッチレス切替：ホバーでタブ切り替え",
        "DataPath": "データ保存場所:",
        "ChangePath": "場所の変更",
        "Reset": "デフォルト設定に戻す (初期化)",
        "ExitApp": "🚪 アプリを完全に終了する",
        
        "SortName": "名前", "SortSize": "サイズ", "SortType": "種類", "SortDate": "更新日時",
        "ViewLargeX": "特大アイコン", "ViewLarge": "大アイコン", "ViewMedium": "中アイコン", "ViewSmall": "小アイコン",
        "MenuSort": "並べ替え   >", "MenuView": "表示   >", "MenuOrg": "🚀 デスクトップ整理", "MenuRestore": "↩️ 元に戻す",
        
        "Lock": "🔒 ボックスをロック", "Unlock": "🔓 ロック解除",
        "ChangeColor": "🎨 色を変更", "OpenSettings": "⚙️ 設定を開く",
        "System": "システム", "Light": "ライト", "Dark": "ダーク",
        "Normal": "通常色", "Transparent": "透明", "Blur": "ぼかし", "Acrylic": "Win11 アクリル",
        "Top": "上部", "Bottom": "下部", "Left": "左側", "Right": "右側"
    }
}

def t(key):
    lang = config.settings.get("language", "zh")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)
