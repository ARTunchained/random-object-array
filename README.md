# random-object-array

Open Source release

Dear users of ROA. Thanks for the ongoing support - you may or may not know that ROA releases always where Open Source / GPL releases, even though the addon was only available through the Blendermarket.

It happened in 2019 that for personal reasons I truly stated before, but no longer want to shout from the rooftops, a lot of things changed in my life. At the same time the Blender Foundation decided to make the jump to Blender 2.8 and turn the Python API upside down without providing documentation. I tried to cope with this as good as possible and released alpha and beta versions of my addons close the 2.8 launch. Later I "hired" an external developer to make the addons fully compatible with 2.8, yet he also wasn't 100% successful - although I'm thankful for his contributions.

Another change in my freelance business happened during that time period and I specialised more and more on IT Security were I see my future career right now.

I'm sorry to say that I can no longer contribute to my own addons, I really hope for someone to pick them up and make them great again. ;) I would love to see one or more of them bundled with Blender in the future.

To any future developer: The code may seem very unclean on first look, but pretty much everything was made on purpose. I developed my own UI / eventhandling process cause "modal operators" didn't fit the ROA workflow at all and the API back then didn't provide anything close to what I needed. The same is true for my loading/saving settings system. Apart from that, each line of code was tested and optimized for speed. CPUs came a long way since 2015 and so did Blender and the API. I still recall that in the beginning I couldn't handle more than a hand full of cubes (about 25) in realtime with Python, while my strongest competitor, the real array modifier, could easily handle thousands. The process was basically like this: I built it in one way, e.g. by using a class or function def. Then I measured latency. Then I rebuilt it without a function, waterfall-style directly into a long loop. If it gave a slight speed advantage I kept it like that, completely ignoring code-quality and other factors. I was painfully aware, that with each new (user-requested or thought-of-by-myself) function the code would be more and more difficult to handle and to debug, in the end I spent days on fixing single issues cause I basically had to re-read and re-learn what I did, each time. Still I put a lot of time, love and dedication into ROA, cause it was the thing I was always missing in Blender, and I'm quite proud of more than a few things, like the fast AABB collision detection algorithm I also wrote from scratch (the theory and other implementations where there already to be fair). 

My suggestion to you would be: Either rewrite from scratch (I know it sucks but at the same time probably 99% of all software ever developed has had the same destiny), or just dive in deep once, fix it as good as possible for 2.8 and call it a day - we already made a lot of the way here already, if you can make the transition from 2.7's groups to collections you're 99% there and made a lot of people, including myself, very happy.

MG
