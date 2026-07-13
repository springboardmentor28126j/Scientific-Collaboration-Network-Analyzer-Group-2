import "dotenv/config";
import { getDb } from "../api/queries/connection";
import { posts, profileBio, cvEntries, localUsers, siteSettings } from "./schema";
import bcrypt from "bcryptjs";

async function seed() {
  console.log("Seeding database...");

  // 1. Seed admin user
  const existingUsers = await getDb().select().from(localUsers);
  if (existingUsers.length === 0) {
    const passwordHash = await bcrypt.hash("123456", 12);
    await getDb().insert(localUsers).values({
      username: "admin",
      passwordHash,
      name: "Admin",
      role: "admin",
    });
    console.log("  Created admin user (admin / 123456)");
  } else {
    console.log("  Admin user already exists");
  }

  // 2. Seed blog posts
  const existingPosts = await getDb().select().from(posts);
  if (existingPosts.length === 0) {
    const seedPosts = [
      {
        year: "2024",
        image: "/images/hero-art.jpg",
        sortOrder: 1,
        zhTitle: "静默的石头",
        zhSubtitle: "关于时间、风化与记忆",
        zhCollection: "自然笔记",
        zhContent: "在一块未经打磨的米白色石灰岩面前，我站了很久。它表面的微孔像月球陨石坑般密集，记录着亿万年前的潮汐与风沙。岩石从不说谎，它只是沉默地展示着时间的纹理。",
        zhDetailContent: "这块石头来自托斯卡纳的一处采石场。初次见到它时，正值黄昏，夕阳从窗户斜射进来，在粗糙的表面投下深浅不一的阴影。那些看似随机的凹陷其实暗藏秩序——每一道刻痕都对应着一次季节性的热胀冷缩，每一个孔洞都曾是某块矿物溶解后留下的印记。\n\n我将它带回工作室，放在一张简单的白桌上。在接下来的三个月里，我每天用不同的光线照射它：清晨的冷光让它呈现出青灰色调，正午的直射光则暴露出更丰富的暖米色层次。\n\n有一次，一位访客问我为什么要花这么多时间凝视一块石头。我没有立即回答，而是递给她一把手电筒，让她从低角度照射石面。当光线平行掠过那些微小的起伏时，整个表面仿佛变成了一幅微缩的地形图——山谷、丘陵、峡谷，应有尽有。\n\n\"石头是凝固的时间，\"我终于说道，\"而我们所做的，不过是学会阅读。\"",
        enTitle: "The Silent Stone",
        enSubtitle: "On Time, Weathering, and Memory",
        enCollection: "Nature Notes",
        enContent: "I stood for a long time before an unpolished piece of off-white limestone. Its surface was densely pocked with craters like the lunar landscape, recording the tides and winds of millions of years ago. Rock never lies \u2014 it simply and silently displays the texture of time.",
        enDetailContent: "This stone came from a quarry in Tuscany. When I first saw it, dusk was settling in, and the setting sun slanted through the window, casting uneven shadows across the rough surface. Those seemingly random depressions concealed an underlying order \u2014 each groove corresponded to a seasonal cycle of thermal expansion and contraction, each cavity was once the imprint left by dissolved minerals.\n\nI brought it back to my studio and placed it on a simple white table. For the next three months, I lit it with different light every day: the cold morning light gave it a bluish-grey tone, while the direct midday sun revealed richer layers of warm beige.\n\nOnce, a visitor asked me why I spent so much time gazing at a stone. I didn't answer immediately. Instead, I handed her a flashlight and asked her to shine it at a low angle across the surface. When the light grazed those tiny undulations in parallel, the entire surface transformed into a miniature topographic map \u2014 valleys, hills, canyons, all present in exquisite detail.\n\n\"Stone is time made solid,\" I finally said. \"And what we do is simply learn to read it.\"",
      },
      {
        year: "2024",
        image: "/images/blog-1.jpg",
        sortOrder: 2,
        zhTitle: "流水的形状",
        zhSubtitle: "长曝光下的自然书写",
        zhCollection: "摄影随笔",
        zhContent: "用三分钟的曝光时间记录一条山间溪流，水流在底片上化作丝绸般的白色丝带。岩石的坚硬与流水的柔软形成永恒的对话——这是自然界最古老的辩证法。",
        zhDetailContent: "去年深秋，我在阿尔卑斯山南麓找到了这条不起眼的小溪。它从冰川融水中诞生，穿过一片冷杉林，最终汇入更大的河流。水量不大，但落差恰到好处，在岩石间形成了层层叠叠的小型瀑布。\n\n我选择了一块略微凸出的岩石作为拍摄点，三脚架支在湿滑的石面上。第一次尝试用了三十秒的曝光，水流呈现出明显的拉丝效果，但还不够梦幻。增加到两分钟后，白色的水带开始融合，形成更连续的形态。最终在三分十五秒时，我找到了理想的平衡点——既保留了岩石的锐利轮廓，又让水流化为飘逸的绸缎。\n\n黑白胶片的选择并非偶然。去除了色彩的干扰，观众的注意力完全被引向形态与质感之间的张力。黑色的岩石是凝固的暴烈，白色的水流是运动的温柔——两者相遇，构成了时间的切片。\n\n冲洗底片的那天，我在暗房里待了整个下午。当影像从显影液中缓缓浮现时，那种期待与惊喜从未因重复而褪色。",
        enTitle: "The Shape of Flowing Water",
        enSubtitle: "Long Exposure as Natural Writing",
        enCollection: "Photography Notes",
        enContent: "I recorded a mountain stream with a three-minute exposure. The flowing water transformed on the negative into silken white ribbons. The hardness of the rock and the softness of the water formed an eternal dialogue \u2014 the oldest dialectic in nature.",
        enDetailContent: "Last late autumn, I found this unremarkable stream on the southern slopes of the Alps. Born from glacial meltwater, it passed through a fir forest before joining a larger river downstream. The water volume was modest, but the gradient was just right, creating layer upon layer of small waterfalls between the rocks.\n\nI chose a slightly protruding rock as my vantage point, planting my tripod on the slippery stone surface. The first attempt at thirty seconds produced a visible streaking effect in the water, but it wasn't yet dreamlike enough. At two minutes, the white bands began to merge into more continuous forms. It was at three minutes and fifteen seconds that I found the ideal balance \u2014 preserving the sharp contours of the rocks while allowing the water to transform into flowing silk.\n\nThe choice of black-and-white film was no accident. Stripped of color's interference, the viewer's attention is drawn entirely to the tension between form and texture. The black rock is frozen violence; the white water is moving gentleness \u2014 where they meet, a slice of time is captured.\n\nOn the day I developed the negatives, I spent the entire afternoon in the darkroom. As the image slowly emerged from the developer, that sense of anticipation and wonder never faded, no matter how many times I had repeated the process.",
      },
      {
        year: "2023",
        image: "/images/blog-2.jpg",
        sortOrder: 3,
        zhTitle: "花园里的众神",
        zhSubtitle: "古典雕塑与当代凝视",
        zhCollection: "艺术档案",
        zhContent: "一座十八世纪的意大利花园里，几尊半身像散落在野草丛中。它们曾代表完美的人体理想，如今却沦为被藤蔓缠绕的废墟。美与衰败之间的落差，恰恰是最动人的部分。",
        zhDetailContent: "这座花园属于一座早已废弃的修道院。据当地档案记载，这些雕塑最初被安置在精心修剪的绿篱迷宫中，每一个转角都安排了一尊古典神祇，为冥想者提供视觉上的锚点。\n\n两百年后，迷宫早已不复存在，取而代之的是肆意生长的荆棘和蕨类。我发现这组雕塑纯属偶然——在当地一位老人的指引下，穿过一片被荨麻覆盖的小径，才到达这个几乎被遗忘的角落。\n\n最令人震撼的是一尊手持里拉琴的女性雕像。她的面部仍然相对完好，但躯干已经缺失了大部分，露出内部粗糙的填充物。阳光透过头顶的树冠洒下来，在她的石膏表面上形成斑驳的光点。那一刻，我突然理解了为什么十八世纪的哲学家如此推崇\"废墟美学\"——不完整本身，比完整更具深意。\n\n我用一台上世纪七十年代的哈苏相机记录了这些画面，胶片的颗粒感与石材的风化纹理形成了一种奇妙的共振。",
        enTitle: "The Gods in the Garden",
        enSubtitle: "Classical Sculpture and Contemporary Gaze",
        enCollection: "Art Archive",
        enContent: "In an eighteenth-century Italian garden, several busts lay scattered among the wild grass. They once embodied the ideal of perfect human form, but now they are ruins entwined with vines. The gap between beauty and decay is precisely what makes them most moving.",
        enDetailContent: "This garden belonged to an abandoned monastery. According to local archives, these sculptures were originally placed within a meticulously trimmed hedge maze, with a classical deity positioned at every turn to provide visual anchors for meditators.\n\nTwo centuries later, the maze had long vanished, replaced by rampant brambles and ferns. I discovered this group of sculptures entirely by chance \u2014 guided by a local elder, I pushed through a path overgrown with nettles to reach this nearly forgotten corner.\n\nThe most striking was a female figure holding a lyre. Her face remained relatively intact, but most of her torso was missing, exposing rough internal filling. Sunlight filtered through the canopy above, creating dappled light patterns across her plaster surface. In that moment, I suddenly understood why eighteenth-century philosophers so admired the \"aesthetics of ruins\" \u2014 incompleteness itself carries more meaning than perfection ever could.\n\nI documented these scenes with a 1970s Hasselblad camera. The film grain resonated curiously with the weathered texture of the stone, creating an unexpected harmony.",
      },
      {
        year: "2023",
        image: "/images/blog-4.jpg",
        sortOrder: 4,
        zhTitle: "城市的墨痕",
        zhSubtitle: "罗夏测试与摩天楼",
        zhCollection: "视觉实验",
        zhContent: "将心理学中的罗夏墨迹测试叠加在城市天际线上，创造出一种介于现实与潜意识之间的视觉场域。建筑的理性秩序与墨迹的混沌随机相遇，产生了意想不到的叙事张力。",
        zhDetailContent: "这个系列的灵感来自一次偶然的叠加。当时我正在整理两种完全不相关的材料：一组是五十年代纽约摩天楼群的仰视照片，另一组是瑞士心理学家罗夏发明的墨迹卡片。两者同时摊开在桌面上，我不小心将一张墨迹卡放在了一张城市照片之上。\n\n效果出乎意料地迷人。墨迹的有机曲线与建筑的刚性线条形成了一种互补关系——就像两个不同频率的声波相遇时产生的拍频现象。墨痕软化了建筑的攻击性，而建筑则为墨痕提供了尺度的参照。\n\n我花了三个月时间系统性地探索这个方向。在暗房里，我用双层放大技术将墨迹底片与城市底片精确叠合。每一次曝光都是一次赌博：两种影像的密度差异、对比度比例、尺寸关系都需要反复调试。最成功的那几张，墨迹仿佛本来就属于天空的一部分——它是云朵的异化形态，也是城市集体潜意识的视觉化呈现。\n\n有观者问我这些作品是否在表达\"城市病了\"。我不确定这是否是我的本意。也许更准确的说法是：城市和人一样，也有它不愿被正视的内在风景。",
        enTitle: "Ink Marks on the City",
        enSubtitle: "Rorschach Tests and Skyscrapers",
        enCollection: "Visual Experiments",
        enContent: "I overlaid Rorschach inkblot tests from psychology onto a city skyline, creating a visual field suspended between reality and the subconscious. Where the rational order of architecture meets the chaotic randomness of ink, unexpected narrative tension is born.",
        enDetailContent: "This series was born from an accidental overlay. At the time, I was organizing two entirely unrelated materials: a set of upward-looking photographs of 1950s New York skyscrapers, and Rorschach inkblot cards invented by the Swiss psychologist. Both spread out on my desk, I accidentally placed an inkblot card on top of a city photograph.\n\nThe result was unexpectedly captivating. The organic curves of the ink complemented the rigid lines of architecture \u2014 like the beat frequency produced when two sound waves of different frequencies meet. The ink softened the aggression of the buildings, while the buildings provided a scale of reference for the ink.\n\nI spent three months systematically exploring this direction. In the darkroom, I used double enlargement techniques to precisely overlay inkblot negatives with city negatives. Each exposure was a gamble: the density difference, contrast ratio, and scale relationship between the two images required endless fine-tuning. In the most successful prints, the ink appeared to have always belonged in the sky \u2014 an alienated form of cloud, a visual manifestation of the city's collective subconscious.\n\nA viewer once asked if these works suggest that \"the city is sick.\" I'm not sure that was my intention. Perhaps a more accurate statement would be: like people, cities also have inner landscapes they would rather not confront.",
      },
      {
        year: "2024",
        image: "/images/blog-5.jpg",
        sortOrder: 5,
        zhTitle: "土与火",
        zhSubtitle: "两尊陶罐的制作札记",
        zhCollection: "手作记录",
        zhContent: "在景德镇的半个月里，我跟随一位老匠人学习拉坯。这两只带有火焰形盖子的陶罐是我的毕业作品——粗粝的赤陶表面保留着指尖的捏痕，那是人与泥土之间最直接的对话痕迹。",
        zhDetailContent: "到达景德镇的那个清晨下着小雨，空气中有泥土被浸润后特有的气息。我住在老厂附近的一间民宿，每天早上步行穿过一条石板路去工作室，路边摆满了等待烧制的半成品。\n\n教我拉坯的师傅姓王，已经做了四十年的陶瓷。他的双手布满细小的伤痕，但动作却精准得像是数控机床。\"拉坯不是用力量，是用呼吸，\"他说，\"你的气息决定了泥土的厚度。\"\n\n这两只陶罐是最后一周的作品。我刻意保持了粗粝的表面处理，没有上釉，让赤陶的自然质感直接呈现。盖子设计成火焰的形状，灵感来自我在当地一座宋代窑址看到的出土器物。古代的陶工似乎相信，容器不仅仅是容器，它还应该暗示某种超越性的力量。\n\n烧制的过程最是煎熬。一千两百度的窑火将泥土转化为石头，这个过程中任何微小的失误——温度不均、升温过快、窑内气氛不对——都可能导致前功尽弃。等待冷却的三十六个小时里，我几乎无法入睡。\n\n开窑的那一刻，火焰形盖子在晨光中呈现出温暖的赭石色。它们的表面不完美，有些地方甚至带着细微的裂纹，但那正是手工制作的灵魂所在。",
        enTitle: "Earth and Fire",
        enSubtitle: "Notes on Making Two Clay Vessels",
        enCollection: "Craft Notes",
        enContent: "During two weeks in Jingdezhen, I studied wheel-throwing under a master craftsman. These two terracotta vessels with flame-shaped lids are my graduation pieces \u2014 their rough surfaces still bear the imprint of fingertips, the most direct trace of dialogue between human hands and clay.",
        enDetailContent: "The morning I arrived in Jingdezhen, a light rain was falling. The air carried that distinctive scent of dampened earth. I stayed at a guesthouse near the old factory, walking every morning along a stone path to the studio, passing rows of half-finished pieces awaiting their turn in the kiln.\n\nMy throwing instructor, surnamed Wang, had been making ceramics for forty years. His hands were covered with tiny scars, yet his movements were as precise as a CNC machine. \"Throwing isn't about force,\" he said, \"it's about breath. Your breath determines the thickness of the clay.\"\n\nThese two vessels were my final-week pieces. I deliberately kept the surface treatment rough, without glaze, allowing the natural texture of the terracotta to speak for itself. The flame-shaped lids were inspired by artifacts I saw at a local Song dynasty kiln site. Ancient potters seemed to believe that a vessel was more than a vessel \u2014 it should hint at some transcendent force.\n\nThe firing process was the most agonizing part. At twelve hundred degrees, the kiln transforms clay into stone, and any minute error \u2014 uneven temperature, too-rapid heating, wrong atmosphere \u2014 could ruin everything. During the thirty-six-hour cooling wait, I could barely sleep.\n\nThe moment I opened the kiln, the flame-shaped lids glowed warm ochre in the morning light. Their surfaces were imperfect, some with fine cracks, but that is precisely the soul of handmade work.",
      },
      {
        year: "2023",
        image: "/images/blog-6.jpg",
        sortOrder: 6,
        zhTitle: "让花朵说话",
        zhSubtitle: "一本关于植物的私人手账",
        zhCollection: "生活随笔",
        zhContent: "春天在院子里采摘的三色堇，被小心地压进了一本旧书的扉页。六个月后，花瓣已经干枯变色，但仍然保持着大致的形状。我在旁边写下了关于那个下午的感受——阳光、微风、和一只停在栏杆上的知更鸟。",
        zhDetailContent: "这本手账开始于去年三月的一个无所事事的日子。那天下午，我坐在花园里晒太阳，注意到石缝间长出了一株小小的三色堇。它的紫色花瓣在灰白色的石材衬托下显得格外醒目，像是一个闯入者，又像是一个信使。\n\n我小心翼翼地把它挖出来，夹进随身携带的笔记本里。回家后，我用一台老式打字机写下了当时的心情。此后的一年里，这本手账成了我记录各种微小发现的容器：一片形状像心形的橡树叶、一根带着树脂香气的松针、一粒不知名植物的种子。\n\n每一页都遵循相同的格式：左边是压制干燥的植物标本，右边是手写或打印的文字。我尝试用不同颜色的墨水来对应不同季节采集的标本——春天的用翠绿色，夏天的用深褐色，秋天的用赭石色，冬天的用灰蓝色。\n\n这本手账没有预设的主题或目的。它只是一个容器，用来安放那些在日常生活中容易被忽略的瞬间。有一次朋友翻看它时说，这些页面让人想起十八世纪的植物学图谱。我告诉她，区别在于那些图谱追求的是科学的精确，而我追求的只是存在的证据。\n\n也许这就是记录的意义——不是为了被展示，而是为了在某个遗忘的午后，重新遇见曾经的自己。",
        enTitle: "Let the Flowers Speak",
        enSubtitle: "A Private Journal of Plants",
        enCollection: "Life Notes",
        enContent: "A pansy picked from the garden in spring was carefully pressed into the flyleaf of an old book. Six months later, the petals had dried and changed color, yet still held their approximate shape. Beside it, I wrote about that afternoon \u2014 the sunlight, the breeze, and a robin perched on the railing.",
        enDetailContent: "This journal began on a March afternoon last year, a day with nothing in particular to do. I was sitting in the garden, soaking up the sun, when I noticed a tiny pansy growing in the crack between stones. Its purple petals stood out vividly against the grey-white stone, like an intruder, or perhaps a messenger.\n\nI carefully dug it out and pressed it into the notebook I carried with me. Back home, I wrote about my mood on an old typewriter. For the rest of the year, this journal became a vessel for recording small discoveries: an oak leaf shaped like a heart, a pine needle carrying the scent of resin, an unidentified seed.\n\nEvery page follows the same format: pressed and dried plant specimens on the left, handwritten or typed text on the right. I tried using different colored inks to correspond with the seasons \u2014 emerald green for spring, dark brown for summer, ochre for autumn, grey-blue for winter.\n\nThis journal has no predetermined theme or purpose. It is simply a container for those moments in daily life that are easily overlooked. Once, a friend leafed through it and said the pages reminded her of eighteenth-century botanical atlases. I told her the difference is that those atlases pursued scientific accuracy, while I pursue nothing more than evidence of existence.\n\nPerhaps that is the meaning of keeping records \u2014 not for display, but for the chance, on some forgotten afternoon, to meet your former self again.",
      },
    ];

    for (const post of seedPosts) {
      await getDb().insert(posts).values(post);
    }
    console.log(`  Seeded ${seedPosts.length} blog posts`);
  } else {
    console.log(`  ${existingPosts.length} blog posts already exist`);
  }

  // 3. Seed profile bio
  const existingBio = await getDb().select().from(profileBio);
  if (existingBio.length === 0) {
    await getDb().insert(profileBio).values({
      id: 1,
      zhText: "陈林 / Chen Lin，视觉艺术家与写作者，现居上海。创作围绕自然材料、摄影工艺与手工技艺展开，试图在最朴素的物质中发现被日常所遮蔽的诗意。从托斯卡纳的石灰岩到景德镇的赤陶，从阿尔卑斯山的冰川溪流到欧洲花园里风化百年的雕塑——我相信记录本身就是创作，而凝视是一种需要反复练习的能力。曾在空白画廊担任驻留艺术家，作品被国内外多个美术馆与私人收藏。闲暇时经营一本植物手账，用不同季节的墨水记录那些容易被遗忘的微小瞬间。",
      enText: "Chen Lin, visual artist and writer, based in Shanghai. My practice revolves around natural materials, photographic processes, and handmade crafts \u2014 seeking the poetry concealed by the everyday within the most humble substances. From the limestone of Tuscany to the terracotta of Jingdezhen, from glacial streams in the Alps to century-weathered sculptures in European gardens \u2014 I believe that recording is itself a form of creation, and that the act of looking is a skill that requires repeated practice. Former artist-in-residence at BLANKSPACE Gallery, with works collected by museums and private collectors at home and abroad. In my spare time, I keep a botanical journal, using inks of different seasons to record those tiny moments easily forgotten.",
      email: "lin.chen@studio.com",
      instagram: "https://instagram.com",
    });
    console.log("  Seeded profile bio");
  } else {
    console.log("  Profile bio already exists");
  }

  // 4. Seed CV entries
  const existingCv = await getDb().select().from(cvEntries);
  if (existingCv.length === 0) {
    const seedCv = [
      { category: "Education", zhTitle: "中国美术学院", zhSubtitle: "跨媒体艺术学院 / 硕士", enTitle: "China Academy of Art", enSubtitle: "School of Intermedia Arts / MFA", year: "2019 - 2022", sortOrder: 1 },
      { category: "Education", zhTitle: "中央美术学院", zhSubtitle: "摄影系 / 学士", enTitle: "Central Academy of Fine Arts", enSubtitle: "Department of Photography / BFA", year: "2015 - 2019", sortOrder: 2 },
      { category: "Employment", zhTitle: "独立工作室", zhSubtitle: "视觉艺术创作 / 上海", enTitle: "Independent Studio", enSubtitle: "Visual Art Practice / Shanghai", year: "2022 - 至今", sortOrder: 3 },
      { category: "Employment", zhTitle: "空白画廊", zhSubtitle: "驻留艺术家 / 景德镇", enTitle: "BLANKSPACE Gallery", enSubtitle: "Artist-in-Residence / Jingdezhen", year: "2023 (3\u4e2a\u6708)", sortOrder: 4 },
      { category: "Employment", zhTitle: "原美术馆", zhSubtitle: "策展助理 / 重庆", enTitle: "Yuan Art Museum", enSubtitle: "Curatorial Assistant / Chongqing", year: "2021 - 2022", sortOrder: 5 },
      { category: "Exhibition", zhTitle: "\u201c\u571f\u4e0e\u8bd7\u201d \u4e2a\u4eba\u5c55\u89c8", zhSubtitle: "BLANKSPACE 画廊 / 上海", enTitle: "\u201cEarth and Poetry\u201d Solo Exhibition", enSubtitle: "BLANKSPACE Gallery / Shanghai", year: "2024", sortOrder: 6 },
      { category: "Exhibition", zhTitle: "\u201c\u65f6\u95f4\u7684\u7eb9\u7406\u201d \u7fa4\u5c55", zhSubtitle: "当代美术馆 / 杭州", enTitle: "\u201cThe Texture of Time\u201d Group Show", enSubtitle: "Contemporary Art Museum / Hangzhou", year: "2023", sortOrder: 7 },
      { category: "Exhibition", zhTitle: "\u201c\u81ea\u7136\u4e66\u5199\u201d \u53cc\u4e2a\u5c55", zhSubtitle: "藝術門画廊 / 香港", enTitle: "\u201cNatural Writing\u201d Duo Exhibition", enSubtitle: "Pearl Lam Galleries / Hong Kong", year: "2023", sortOrder: 8 },
      { category: "Exhibition", zhTitle: "\u201c\u65b0\u9510\u89c6\u89d2\u201d \u5e74\u5ea6\u5c55", zhSubtitle: "今日美术馆 / 北京", enTitle: "\u201cEmerging Perspectives\u201d Annual Show", enSubtitle: "Today Art Museum / Beijing", year: "2022", sortOrder: 9 },
      { category: "Awards", zhTitle: "青年艺术家资助计划", zhSubtitle: "获选艺术家 / 提名", enTitle: "Young Artist Fellowship Program", enSubtitle: "Selected Artist / Nominee", year: "2024", sortOrder: 10 },
      { category: "Awards", zhTitle: "三影堂摄影奖", zhSubtitle: "入围 / 策展人特别推荐", enTitle: "Three Shadows Photography Award", enSubtitle: "Shortlisted / Curator's Special Mention", year: "2023", sortOrder: 11 },
      { category: "Awards", zhTitle: "新锐摄影奖", zhSubtitle: "TOP 20", enTitle: "New Talent Photography Award", enSubtitle: "TOP 20", year: "2022", sortOrder: 12 },
      { category: "Press", zhTitle: "\u201c\u5728\u65e5\u5e38\u4e2d\u5bfb\u627e\u795e\u6027\u201d", zhSubtitle: "ArtReview Asia / 专访", enTitle: "\u201cFinding the Divine in the Everyday\u201d", enSubtitle: "ArtReview Asia / Interview", year: "2024", sortOrder: 13 },
      { category: "Press", zhTitle: "\u201c\u4e00\u4f4d\u7528\u624b\u601d\u8003\u7684\u827a\u672f\u5bb6\u201d", zhSubtitle: "艺术界 LEAP / 专题", enTitle: "\u201cAn Artist Who Thinks With Her Hands\u201d", enSubtitle: "LEAP / Feature", year: "2023", sortOrder: 14 },
      { category: "Press", zhTitle: "\u201c\u9759\u9ed8\u7684\u529b\u91cf\u201d", zhSubtitle: "画刊 / 评论", enTitle: "\u201cThe Power of Silence\u201d", enSubtitle: "Art Magazine / Review", year: "2023", sortOrder: 15 },
      { category: "Press", zhTitle: "\u201c\u5f53\u77f3\u5934\u5f00\u59cb\u8bf4\u8bdd\u201d", zhSubtitle: "艺术当代 / 评论", enTitle: "\u201cWhen Stones Begin to Speak\u201d", enSubtitle: "Art China / Review", year: "2022", sortOrder: 16 },
    ];

    for (const entry of seedCv) {
      await getDb().insert(cvEntries).values(entry);
    }
    console.log(`  Seeded ${seedCv.length} CV entries`);
  } else {
    console.log(`  ${existingCv.length} CV entries already exist`);
  }

  // 5. Seed site settings
  const existingSettings = await getDb().select().from(siteSettings);
  if (existingSettings.length === 0) {
    await getDb().insert(siteSettings).values({
      id: 1,
      avatarImage: "/images/portrait.jpg",
    });
    console.log("  Seeded site settings");
  } else {
    console.log("  Site settings already exist");
  }

  console.log("Seed complete!");
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
