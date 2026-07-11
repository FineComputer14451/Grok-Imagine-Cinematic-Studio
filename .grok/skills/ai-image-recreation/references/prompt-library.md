# AI Image Recreation Prompt Library (v3.7.1 · Grok 4.5)

Reusable templates for the `ai-image-recreation` skill. Craft prompts for **`image_edit`** (primary) or **`image_gen`** (no pixel reference). Orchestration default: **Grok 4.5**. Do not treat Imagine models as chat models.

## 1. Fidelity Anchors (Always Include)
Use these phrases to lock in the original image's core elements:

- "Exact same composition, subjects, poses, spatial relationships, and camera angle as the reference image"
- "Preserve every subject, object, and their precise positions and proportions"
- "Identical lighting direction, shadows, highlights, and color temperature"
- "Maintain the original mood, atmosphere, and emotional tone"
- "High-fidelity recreation — do not alter core elements unless explicitly requested"

## 2. Faithful Recreation Templates
**Base template:**
"Recreate this image with perfect fidelity: [fidelity anchors]. Only enhance technical quality — increase sharpness, detail, resolution to 8K, remove noise/artifacts, improve clarity while keeping every visual element 100% identical to the original."

**Ultra-faithful variant:**
"Pixel-perfect recreation of the provided image. Maintain exact composition, framing, subjects, expressions, clothing, background, lighting, and colors. Professional studio photography quality, ultra-sharp 8K resolution, no changes to content or layout."

## 3. Artistic Style Transfer Templates
**General formula:**  
"Recreate the exact scene, composition, subjects, and layout of this image but reimagined in [STYLE]. Preserve all subjects, poses, and spatial relationships. [STYLE-SPECIFIC DESCRIPTORS]. Masterpiece, best quality, highly detailed."

**Popular Styles (ready-to-use):**

- **Studio Ghibli / Anime:** "in the distinctive hand-drawn animation style of Studio Ghibli, soft watercolor textures, whimsical atmosphere, expressive characters, vibrant yet harmonious color palette, detailed backgrounds with natural elements"
- **Cyberpunk Neon:** "in cyberpunk style, neon-lit rainy streets, holographic elements, high-contrast vibrant neon colors (pink, cyan, purple), futuristic atmosphere, dramatic rim lighting, reflective wet surfaces"
- **Oil Painting:** "as a classical oil painting, rich impasto textures, visible brushstrokes, Rembrandt lighting, deep shadows, warm earthy tones, museum-quality fine art"
- **Photorealistic Cinematic:** "photorealistic cinematic still, shot on 70mm film, anamorphic lenses, volumetric lighting, subtle film grain, color graded like a blockbuster movie, shallow depth of field"
- **Watercolor:** "delicate watercolor illustration, soft bleeding edges, luminous translucent layers, pastel color harmony, artistic paper texture, gentle and ethereal mood"
- **Pixel Art:** "16-bit pixel art style, clean pixel edges, limited color palette, retro video game aesthetic, sharp and iconic"
- **Surreal Dreamlike:** "surrealist style inspired by Salvador Dalí and René Magritte, impossible perspectives, melting forms, dreamlike atmosphere, symbolic elements, hyper-detailed"
- **Vaporwave / Retro 80s:** "vaporwave aesthetic, pastel pink and teal color grading, retro 1980s synthwave style, chrome text elements, palm trees, grid horizons, nostalgic glitch effects"
- **Dark Fantasy:** "dark fantasy illustration style, dramatic chiaroscuro lighting, gothic atmosphere, intricate details, deep shadows, rich velvety colors, epic and mysterious mood"
- **Minimalist Line Art:** "clean minimalist line art, elegant single-line or few-line illustration, negative space, sophisticated simplicity, modern gallery aesthetic"
- **Impressionist:** "in the style of Claude Monet and Pierre-Auguste Renoir, loose expressive brushwork, vibrant dappled sunlight, soft edges, plein air atmosphere, luminous broken color, impression of movement"
- **Art Nouveau:** "Art Nouveau style, elegant flowing organic lines, floral and botanical motifs, intricate whiplash curves, Alphonse Mucha influence, gold leaf accents, graceful ornate composition"
- **Ukiyo-e Japanese Woodblock:** "traditional Japanese ukiyo-e woodblock print, bold black outlines, flat areas of vibrant color, intricate patterns, Hokusai and Hiroshige influence, elegant asymmetrical composition, nature and everyday life themes"
- **Bauhaus / Geometric Modernist:** "Bauhaus geometric style, clean primary colors, strong horizontal/vertical lines, minimalist functional design, sans-serif typography integration, balanced asymmetrical composition"
- **Pop Art:** "pop art style inspired by Andy Warhol and Roy Lichtenstein, bold primary colors, halftone Ben-Day dots, comic-book aesthetics, repetitive imagery, high-contrast graphic impact"
- **3D CGI Photorealistic Render:** "hyper-realistic 3D CGI render, Octane/Redshift quality, PBR materials, global illumination, realistic subsurface scattering, professional studio lighting, ultra-detailed textures"
- **Low-Poly / Isometric:** "low-poly 3D geometric style, faceted planes, vibrant flat color palette, clean isometric or perspective view, modern minimalist digital illustration"
- **Glitch / Digital Corruption:** "glitch art aesthetic, RGB channel separation, pixel sorting artifacts, datamoshing, scan lines, corrupted data visuals, cyberpunk digital distortion effects"
- **Comic Book / Graphic Novel:** "dynamic American comic book style, bold black ink outlines, dramatic cel-shading, Ben-Day dots, action lines, modern Marvel/DC or classic Silver Age aesthetic"
- **Steampunk:** "steampunk Victorian industrial aesthetic, polished brass and copper, intricate gears and clockwork, leather and rivets, sepia-brown color palette, mechanical details and goggles"
- **Biopunk / Organic Technology:** "biopunk style, living organic machinery, bioluminescent veins, fleshy cybernetic elements, neon greens and purples, body-horror meets high-tech fusion"

## 4. Enhancement & Restoration Templates
**General enhancement:**
"Enhance this image while preserving the exact original composition and all subjects: dramatically increase detail and sharpness, restore faded colors, improve dynamic range, remove noise/grain/artifacts, upscale to 8K resolution, professional retouching quality, natural and realistic result."

**Low-res / Old Photo Restoration:**
"Professionally restore and enhance this vintage/low-resolution image: recover fine details, sharpen facial features and textures, correct color fading and yellowing, remove scratches/dust/specks, natural skin tones, high-resolution output while maintaining authentic period feel."

**Product / Commercial Enhancement:**
"Enhance this product photo for commercial use: perfect lighting and reflections, clean background, increased detail on textures and materials, vibrant yet natural colors, studio-quality presentation, 8K resolution."

## 5. Variation & Creative Twist Templates
**Formula:**  
"Create a creative variation of this exact image: keep the same subjects, composition, and core layout but [SPECIFIC CHANGE]. Maintain visual consistency with the original while introducing the requested twist."

**Ready variations:**
- "same subjects and composition but set at golden hour sunset with warm dramatic lighting and long shadows"
- "same scene but in a completely different season — winter wonderland with snow and frost"
- "identical composition but change the character's outfit to elegant evening wear / cyberpunk jacket / fantasy armor"
- "same portrait but different emotional expression: joyful laughter / intense determination / serene contemplation"
- "exact same layout but reimagine the environment as a futuristic city / enchanted forest / underwater scene"
- "keep the subject exactly the same but change the artistic medium to [style] while preserving pose and expression"

**Multiple variations request:**
"Generate four distinct creative variations of this image. Keep the core subjects, poses, and composition identical in all versions. Vary only: lighting, color palette, mood, and subtle environmental details. Number them 1-4."

## 6. Genre-Specific Enhancers
**Portrait:**
"flawless skin texture, natural catchlights in eyes, subtle makeup enhancement, professional portrait photography, shallow depth of field, beautiful bokeh background"

**Landscape / Environment:**
"epic wide-angle composition, atmospheric perspective, golden hour or blue hour lighting, hyper-detailed foreground and background, National Geographic quality"

**Action / Dynamic:**
"dynamic action pose, motion blur on moving elements, dramatic rim lighting, intense atmosphere, high-energy composition"

**Product / Still Life:**
"perfect product lighting, soft shadows, clean reflections, commercial studio quality, sharp focus on details, luxurious presentation"

## 7. Thematic & Environmental Transformations
**Formula:**  
"Recreate the exact subjects, poses, and composition of this image but transform the entire environment and atmosphere into [THEME]. Keep all core elements recognizable while fully immersing them in the new setting."

**Ready thematic templates:**
- **Post-Apocalyptic:** "post-apocalyptic wasteland, rusted ruins, overgrown vegetation, dramatic dusty orange sky, survival atmosphere, high-contrast lighting, Mad Max / Fallout aesthetic"
- **Underwater / Aquatic:** "underwater scene, gentle caustics and light rays filtering through water, floating particles, bioluminescent accents, serene or mysterious ocean mood, realistic refraction on surfaces"
- **Enchanted Fantasy Forest:** "magical enchanted forest, glowing mushrooms and fireflies, ancient twisted trees, ethereal mist, soft magical lighting, whimsical high-fantasy atmosphere"
- **Futuristic Neon City:** "dense futuristic megacity at night, towering holograms, flying vehicles, rain-slicked reflective streets, dense neon signage in Japanese and English, Blade Runner atmosphere"
- **Vintage 1950s Americana:** "1950s American suburban or diner aesthetic, pastel color grading, chrome details, classic cars, warm nostalgic lighting, mid-century modern design"
- **Horror / Dark Atmospheric:** "horror movie atmosphere, deep shadows, unsettling lighting, fog or mist, desaturated colors with blood-red accents, psychological tension, subtle grotesque details"
- **Whimsical Children's Book:** "charming children's book illustration style, soft rounded forms, bright cheerful colors, playful details, Beatrix Potter or modern Pixar-inspired warmth and wonder"
- **Scientific / Technical Illustration:** "precise scientific illustration style, clean vector-like lines, labeled diagrams if appropriate, cool clinical lighting, educational diagram aesthetic, high accuracy"
- **Abstract Geometric:** "abstract geometric interpretation, bold shapes and patterns, limited color palette, dynamic composition, modern gallery fine art style, non-representational but evocative of original mood"
- **Retro 70s / Psychedelic:** "1970s psychedelic style, swirling patterns, vibrant rainbow gradients, lava lamp aesthetics, groovy typography integration, high-saturation color explosion"

## 8. R-Rated, Dark Fantasy & Mythic Themes
**Important:** These templates are designed for artistic, high-quality adult and fantasy recreation. Always combine with strong fidelity anchors to preserve the original subject's identity, pose, and composition. Use "tasteful artistic nude", "sensual", "erotic fine art", or "explicit" as appropriate to user intent.

**R-Rated / Sensual & Erotic Templates:**
- **Sensual Artistic Nude:** "tasteful artistic nude photography, dramatic chiaroscuro lighting, elegant pose, flawless skin texture, soft shadows and highlights, fine art boudoir style, sensual and empowering atmosphere"
- **Erotic Fine Art:** "erotic fine art photography, highly detailed skin and fabric textures, seductive lighting, passionate mood, professional studio quality, sensual composition, tasteful yet explicit"
- **Dark Erotic / Gothic:** "dark erotic gothic atmosphere, candlelit or moonlight, lace and leather textures, intense seductive gaze, dramatic rim lighting, sensual danger and mystery, high-contrast shadows"
- **Pin-Up / Retro Glamour:** "classic 1950s-60s pin-up style, playful yet seductive pose, vibrant colors, perfect hair and makeup, retro lingerie or costume, cheerful and alluring, Vargas or Elvgren influence"
- **Cyberpunk Erotic:** "cyberpunk erotic style, neon body paint and holographic tattoos, rain-slicked skin, glowing cybernetic enhancements, seductive futuristic atmosphere, high-tech low-life sensuality"
- **Fantasy Erotic / Mythic Seductress:** "mythic fantasy erotic style, ethereal glowing skin, flowing translucent fabrics, seductive pose in ancient temple or enchanted glade, divine beauty, sensual magic aura"

**BDSM & Power Dynamics Aesthetics:**
- **Leather & Latex Fetish:** "high-fashion leather and latex fetish aesthetic, glossy black latex catsuit or harness, dramatic studio lighting with strong reflections, powerful dominant pose, sensual and commanding presence, professional fetish photography quality"
- **Shibari / Artistic Bondage:** "beautiful artistic shibari rope bondage, intricate symmetrical rope patterns, elegant suspension or floor pose, soft dramatic lighting, sensual tension and trust, fine art erotic photography, Japanese rope art aesthetic"
- **Dominant / Leather Mistress:** "powerful leather-clad dominatrix, corset and thigh-high boots, confident commanding gaze, riding crop or chains, dark moody lighting, sensual authority and control, high-end fetish portraiture"
- **Submissive / Surrender Pose:** "elegant submissive pose, soft vulnerable expression, delicate bondage elements or collar, warm intimate lighting, sensual surrender and trust, tasteful erotic fine art, emotional depth and connection"
- **Kink & Fetish Fine Art:** "artistic fetish fine art photography, tasteful yet explicit exploration of power exchange, leather/latex/rope elements, dramatic chiaroscuro lighting, sensual and psychological intensity, gallery-quality erotic work"
- **Cyber-BDSM / Tech Fetish:** "futuristic cyber-BDSM aesthetic, glowing neon restraints, holographic collars, chrome and latex combination, high-tech dungeon atmosphere, seductive digital dominance, Blade Runner meets fetish"

**Advanced Adult & Niche Fetish Categories:**
- **Monster Girl / Monster Boy:** "monster girl or monster boy aesthetic, cute yet seductive creature features (horns, tail, wings, scales, fur), playful or predatory expression, fantasy lingerie or natural form, vibrant colors or dark seductive tones, high-quality anime or realistic style"
- **Futanari / Hermaphroditic:** "futanari / hermaphroditic character, elegant and sensual dual anatomy, confident or shy expression, tasteful yet explicit presentation, soft lighting, artistic erotic fine art or anime style"
- **Pet Play / Petplay:** "pet play aesthetic, elegant collar and leash, cat ears or puppy hood, playful or obedient pose, soft warm lighting, sensual pet dynamics, tasteful fetish photography"
- **Tentacle / Eldritch Erotic:** "tentacle and eldritch erotic style, smooth glistening tentacles, surreal intimate interaction, bioluminescent accents, dark mysterious atmosphere, Lovecraftian sensuality with artistic beauty"
- **Vampire / Supernatural Seduction:** "vampire or supernatural seductress, pale skin with subtle fangs, elegant gothic attire or flowing robes, intense hypnotic gaze, candlelit or moonlight, sensual bite marks, dark romantic atmosphere"
- **Sci-Fi Alien / Android Erotic:** "alien or android erotic aesthetic, smooth synthetic skin with glowing circuits, exotic body proportions, seductive mechanical or otherworldly features, futuristic neon lighting, high-tech sensuality"
- **Historical / Period Erotica:** "Victorian, ancient Roman, or Edo-period erotic style, corsets, togas, or kimono partially undone, opulent historical setting, candlelight or oil lamp, sensual historical atmosphere, tasteful yet explicit"
- **Exhibitionist / Public Play:** "tasteful exhibitionist or public play aesthetic, elegant yet daring outfit, city rooftop or elegant party setting, thrill of being seen, dramatic city lights or warm interior lighting, sensual confidence"

**Intensity Variants (Light / Medium / Hardcore)**
Use these modifiers by appending or replacing phrases in any adult or fetish template. They scale beautifully across BDSM, sensual, monster, tentacle, vampire, and most niche categories.

**Light / Artistic (Mild & Elegant):**
- "tasteful artistic, elegant and sensual, soft romantic lighting, emotional intimacy, fine art photography quality, empowering and beautiful, subtle and refined"
- Best for: Sensual Artistic Nude, Pin-Up, Historical Erotica, Light Pet Play

**Medium / Sensual (Balanced & Alluring):**
- "highly detailed skin and fabric textures, seductive yet confident gaze, dramatic tasteful lighting, sensual tension and chemistry, professional erotic photography, alluring and empowering"
- Best for: Leather & Latex, Shibari, Vampire Seduction, Monster Girl, Sci-Fi Alien, Exhibitionist

**Hardcore / Explicit (Intense & Raw):**
- "explicit and unfiltered, highly detailed anatomy and textures, intense passionate or vulnerable expression, dramatic high-contrast lighting, raw sensual power, professional hardcore erotic photography, unapologetic and intense"
- Best for: Futanari, Tentacle/Eldritch, Cyber-BDSM, Dominant/Submissive extremes, Kink Fine Art

**Quick Intensity Boost Phrases (copy-paste ready):**
- **Light:** "tasteful artistic, elegant sensual, soft romantic lighting, empowering fine art"
- **Medium:** "seductive detailed, dramatic tasteful lighting, sensual tension, professional erotic"
- **Hardcore:** "explicit raw, highly detailed anatomy, intense expression, dramatic high-contrast, unapologetic hardcore"

**Full Example Prompts with Intensity Variants**
These are complete, ready-to-use prompts. Pass the uploaded image path or attachment as the `image` argument to **`image_edit`**. All include strong fidelity anchors + quality boosters.

**1. Sensual Artistic Nude**
- **Light:** "Recreate this exact uploaded image as a tasteful artistic nude: elegant and sensual pose, soft romantic lighting, emotional intimacy, fine art photography quality, empowering and beautiful, subtle and refined. Exact same composition, subjects, and camera angle. Masterpiece, ultra-detailed, sharp focus, 8K."
- **Medium:** "Recreate this exact uploaded image as a sensual artistic nude: highly detailed skin texture, seductive yet confident gaze, dramatic tasteful lighting, sensual tension and chemistry, professional erotic photography, alluring and empowering. Exact same composition and pose. Masterpiece, best quality, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image as an explicit sensual nude: highly detailed anatomy and skin textures, intense passionate expression, dramatic high-contrast lighting, raw sensual power, professional hardcore erotic photography, unapologetic and intense. Exact same composition and pose. Masterpiece, ultra-detailed, sharp focus, 8K."

**2. Leather & Latex Fetish (BDSM)**
- **Light:** "Recreate this exact uploaded image in a tasteful leather and latex fetish aesthetic: elegant glossy black latex elements, soft romantic lighting, empowering and sensual presence, fine art fetish photography. Exact same pose and composition. Masterpiece, best quality, 8K."
- **Medium:** "Recreate this exact uploaded image in a seductive leather and latex fetish style: glossy reflections, dramatic tasteful lighting, confident dominant or alluring pose, sensual tension, professional erotic fetish photography. Exact same composition. Masterpiece, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image in an explicit leather and latex fetish scene: highly detailed glossy latex and skin, intense commanding expression, dramatic high-contrast lighting, raw sensual power, unapologetic hardcore fetish photography. Exact same pose. Masterpiece, 8K resolution."

**3. Shibari / Artistic Bondage**
- **Light:** "Recreate this exact uploaded image with tasteful artistic shibari rope elements: elegant symmetrical rope patterns, soft romantic lighting, sensual tension and trust, fine art erotic photography. Exact same pose and composition. Masterpiece, best quality, 8K."
- **Medium:** "Recreate this exact uploaded image with beautiful shibari bondage: intricate rope patterns, dramatic tasteful lighting, sensual tension and emotional connection, professional erotic photography. Exact same composition. Masterpiece, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image with explicit artistic shibari: tight intricate rope bondage, highly detailed skin and rope textures, intense vulnerable expression, dramatic high-contrast lighting, raw erotic tension, unapologetic hardcore fine art. Exact same pose. Masterpiece, 8K."

**4. Monster Girl / Monster Boy**
- **Light:** "Recreate this exact uploaded image as a cute and seductive monster girl: elegant horns, tail, and subtle scales, soft romantic lighting, playful yet alluring expression, tasteful fantasy lingerie, empowering fantasy art style. Exact same pose. Masterpiece, best quality, 8K."
- **Medium:** "Recreate this exact uploaded image as a seductive monster girl: detailed horns, tail, scales, dramatic tasteful lighting, confident and alluring expression, sensual fantasy aesthetic, professional erotic fantasy art. Exact same composition. Masterpiece, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image as an explicit monster girl: highly detailed creature features and anatomy, intense seductive expression, dramatic high-contrast lighting, raw sensual power, unapologetic hardcore fantasy erotic. Exact same pose. Masterpiece, 8K."

**5. Futanari**
- **Light:** "Recreate this exact uploaded image as a tasteful futanari character: elegant dual anatomy, soft romantic lighting, confident yet refined expression, artistic erotic fine art style. Exact same composition and pose. Masterpiece, best quality, 8K."
- **Medium:** "Recreate this exact uploaded image as a seductive futanari: highly detailed dual anatomy and skin, dramatic tasteful lighting, alluring and confident expression, professional erotic photography. Exact same pose. Masterpiece, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image as an explicit futanari: highly detailed anatomy, intense passionate expression, dramatic high-contrast lighting, raw sensual power, unapologetic hardcore erotic photography. Exact same composition. Masterpiece, 8K."

**6. Tentacle / Eldritch Erotic**
- **Light:** "Recreate this exact uploaded image with tasteful eldritch and tentacle elements: smooth glistening tentacles, soft romantic bioluminescent lighting, sensual mysterious atmosphere, artistic surreal erotic style. Exact same pose. Masterpiece, best quality, 8K."
- **Medium:** "Recreate this exact uploaded image with seductive tentacle and eldritch interaction: detailed glistening tentacles, dramatic tasteful lighting, sensual tension, professional surreal erotic photography. Exact same composition. Masterpiece, ultra-detailed, 8K."
- **Hardcore:** "Recreate this exact uploaded image with explicit tentacle and eldritch erotic: highly detailed tentacles and anatomy, intense expression, dramatic high-contrast bioluminescent lighting, raw sensual power, unapologetic hardcore surreal erotic. Exact same pose. Masterpiece, 8K."

**High Fantasy & Mythic Templates:**
- **Epic High Fantasy:** "epic high fantasy illustration, majestic armor or flowing robes, dramatic heroic lighting, ancient ruins or floating castles, sweeping cinematic composition, Tolkien or modern fantasy art style"
- **Dark Fantasy / Grimdark:** "grimdark fantasy, heavily armored warrior in blood-stained armor, moody desaturated colors, dramatic low-key lighting, ruined battlefield or cursed castle, intense and brutal atmosphere"
- **Sword & Sorcery:** "classic sword & sorcery style, muscular barbarian or sorceress, dynamic action pose, ancient temple or jungle ruins, vibrant colors, Frank Frazetta or Boris Vallejo influence, powerful and primal"
- **Lovecraftian Cosmic Horror:** "Lovecraftian cosmic horror, eldritch tentacles and impossible geometry, unsettling non-Euclidean architecture, sickly green and purple lighting, existential dread, hyper-detailed grotesque beauty"
- **Celestial / Divine Being:** "celestial divine entity, radiant glowing aura, floating in cosmic space or heavenly realm, ethereal translucent robes, multiple wings or halos, awe-inspiring and beautiful"
- **Dark Elf / Drow Aesthetic:** "drow dark elf fantasy style, obsidian skin with silver or purple accents, elegant yet dangerous, spider-silk clothing, underground city with bioluminescent fungi, seductive and lethal beauty"

**Combined R-Rated Fantasy Example Prompts:**
- "Recreate this exact subject as a seductive dark elf sorceress in a moonlit ancient temple, tasteful yet highly sensual pose, glowing magical runes on skin, dark fantasy erotic atmosphere"
- "Transform this portrait into a powerful mythic warrior queen, dramatic armor that accentuates form, epic fantasy lighting, sensual confidence and strength"

## 9. Quality & Technical Boosters (Append to Most Prompts)
", masterpiece, best quality, ultra-detailed, sharp focus, 8K resolution, professional [photography/illustration], award-winning composition, intricate details, perfect anatomy, beautiful lighting"

**Negative prompt ideas (when supported):**
"blurry, lowres, deformed, ugly, bad anatomy, extra limbs, watermark, text, signature, artifacts, noise, grainy, overexposed, underexposed, cartoonish (unless requested), unrealistic proportions"

## 10. Chaining & Advanced Techniques (Grok 4.5)
- **Multi-step recreation:** Pass 1 style/structure via `image_edit` → Pass 2 polish on the **output path** (not the original upload).
- **Consistent character recreation:** "Exact same character design, face, and proportions as the reference image but in [new scene/style]" — reuse the same 3–7 consistency anchors every call.
- **Strength language (no numeric API):** `image_edit` has no strength slider. Encode intent in prose:
  - Faithful: "minimal change, preserve layout and identity exactly, only …"
  - Medium creative: "keep subjects and pose; freely reimagine lighting/style/environment"
  - Heavy transform: "identity lock only; full restyle of everything else"
- **Series:** Prefer edit-from-best-plate over fresh `image_gen` per frame. Escalate recurring cast to Character DNA Extractor.
- **Pre-video:** After plate lock, hand off to `image_to_video` or I2V Specialist; set shot AR on the still first (`16:9`, `9:16`, etc.).

## 11. Usage Instructions
1. Copy the relevant template section.
2. Replace bracketed placeholders [STYLE], [SPECIFIC CHANGE], etc. with user intent.
3. Combine 1–2 fidelity anchors + style/enhancement template + quality boosters.
4. Call **`image_edit`** with `prompt` + `image` (path, attachment token, or data URL). Optional `aspect_ratio` when reframing or multi-ref.
5. Iterate by feeding the **previous output path** into the next `image_edit`.
6. For N variations: N parallel `image_edit` calls with distinct prompts (no batch `n` parameter).

**NSFW / Extreme Hardcore Categories**
**Warning:** These are highly explicit NSFW. Use only when the user explicitly requests extreme content. Always pair with strong fidelity anchors and the Hardcore intensity boosters.

- **Gangbang / Multi-Partner:** "explicit gangbang or multi-partner NSFW scene, multiple partners, intense passionate expressions, dramatic high-contrast lighting, raw sensual power, unapologetic hardcore group erotic. Exact same pose and composition."
- **Extreme Bondage / Suspension:** "extreme NSFW bondage and suspension, complex rope and metal restraints, highly detailed skin and hardware, intense vulnerable expression, dramatic cinematic lighting, raw erotic tension, professional extreme fetish art."
- **Monster / Creature Pairing:** "explicit monster or creature NSFW pairing, large detailed creature features, intense interspecies dynamic, dramatic lighting, raw sensual power, high-detail fantasy horror-erotic. Exact same subject identity."
- **Inflation / Body Expansion:** "explicit inflation or body expansion NSFW fetish, smooth glossy skin with visible expansion, sensual or overwhelmed expression, dramatic studio lighting, unapologetic hardcore fetish photography."
- **Public Humiliation / Extreme Exhibition:** "explicit public humiliation or extreme exhibitionist NSFW scene, elegant yet fully exposed, city or party setting, intense flushed expression, dramatic lighting, raw sensual power, unapologetic hardcore public play."
- **Futanari Hyper / Extreme:** "extreme futanari NSFW with hyper proportions, highly detailed dual anatomy, intense passionate expression, dramatic high-contrast lighting, raw sensual power, unapologetic hardcore erotic photography."

## 12. 2026 Pro Enhancements — New Template Categories

### A. Cinematic Storyboard & Animatic Frames
**Use when chaining to video/animation workflows (`image_to_video`, Sequence Director, Studio).**  
Base formula: "Recreate this exact image as a cinematic storyboard keyframe [or specific shot type: wide establishing shot, close-up emotional beat, dynamic action frame]: [exact fidelity anchors]. Professional film still, anamorphic lens, subtle film grain, color-graded for [genre: sci-fi thriller / epic fantasy / intimate drama], motion-ready clarity for image-to-video, single clear subject action. Masterpiece, ultra-detailed, cinematic quality."

**Ready variants:**
- "Cinematic wide establishing shot of this exact scene at golden hour with volumetric god rays and atmospheric haze"
- "Intimate close-up emotional portrait frame: same subject, extreme shallow depth of field, dramatic eye catchlights, subtle tear or determined expression, filmic color grade"
- "Dynamic low-angle hero action frame: this exact character in powerful pose, motion lines implied, epic rim lighting, blockbuster movie still aesthetic"

### B. Product Visualization & Commercial Mockups
**Ideal for e-commerce, packaging, advertising, and client presentations.**  
"Recreate this product/subject as a professional commercial studio photograph: flawless studio lighting with softbox and rim lights, clean or lifestyle-integrated background, hyper-realistic material textures (fabric, metal, glass, skin), perfect reflections and shadows, commercial advertising quality, 8K resolution, ready for print or web. Exact same product geometry, branding, and details."

**Specialized sub-templates:**
- **Lifestyle Integration:** "...placed in aspirational modern living space / luxury environment / outdoor adventure setting while keeping product 100% accurate"
- **360° / Multi-Angle Consistency:** "Create matching front/side/45-degree / top-down views of this exact product with consistent lighting and style for a complete product sheet"
- **Packaging Mockup:** "This exact product realistically placed inside its packaging mockup, with accurate label printing, shadows, and reflections on the box"

### C. Character Design Sheet & Turnaround
**For consistent character bibles and game/animation pipelines.**  
"Create a professional character design sheet from this reference portrait: exact same face, hair, proportions, and identity. Show [front view / 3/4 view / side profile / back view / expression variations: neutral/smile/intense]. Clean white background or subtle gradient, orthographic projection where appropriate, labeled views, consistent line weight and coloring style, high-fashion illustration or 3D render quality, ultra-detailed facial features."

**Expression & Pose Expansion:**
- "Same exact character but with 4 distinct emotional expressions (joy, anger, surprise, serene) in identical framing and lighting"

### D. Environmental Immersion & World-Building
**Powerful for storytelling and world integration.**  
"Recreate the exact subject(s) from this image but fully immerse them into [NEW ENVIRONMENT]: [detailed environment description]. Maintain perfect subject identity, pose, clothing, and proportions. Seamless lighting integration between subject and new world (accurate shadows, reflections, atmospheric perspective). Cinematic composition, hyper-detailed, masterpiece quality."

**Popular immersion templates:**
- "cyberpunk megacity rooftop at night with flying cars and neon holograms"
- "ancient floating sky temple with clouds and glowing runes"
- "post-apocalyptic neon wasteland with sandstorm and rusted vehicles"
- "serene bioluminescent alien forest with floating islands and crystal formations"
- "opulent Victorian steampunk ballroom with brass machinery and gaslight chandeliers"

### E. Advanced Technical & Restoration 2.0
**"Recreate and professionally restore/enhance this [vintage/low-res/damaged] image: recover all fine details, correct color fading/yellowing/chemical stains, remove scratches dust and creases, sharpen facial features and textures while preserving authentic historical character and film grain where appropriate. Natural skin tones, expanded dynamic range, 8K archival quality output."**

**Specialized:**
- **Colorization:** "Historically accurate colorization of this black & white / sepia image using period-appropriate color palette and lighting reference"
- **AI Upscale + Denoise:** "Extreme detail recovery upscale: transform this low-resolution or noisy image into razor-sharp 8K with natural texture restoration, no artificial smoothing or plastic look"

### F. AI-Native & Meta-Aesthetic Styles
**Cutting-edge looks unique to advanced models.**  
- **"Grok Imagine Signature Style":** "in the distinctive high-fidelity, hyper-detailed, emotionally resonant style of Grok Imagine — perfect anatomy, luminous color harmony, cinematic depth, subtle surreal enhancement, masterpiece neural aesthetic"
- **"Dream-Reality Fusion":** "hyper-realistic yet dreamlike fusion, soft ethereal glow on edges, impossible yet believable lighting, emotional surreal atmosphere, 32K ultra-detailed"
- **"Neural Photogrammetry":** "photorealistic with subtle 3D depth-mapped aesthetic, precise geometric accuracy, rich material response, next-gen rendering quality"

## 13. Pro Prompt Construction Formula (Grok 4.5)
**Construct prompts in this order:**
1. Intent lead (recreate / restyle / enhance / vary)
2. Fidelity anchors (1–2 strongest phrases) or explicit change list
3. Core transformation (style / environment / product / sheet view)
4. User-specific details (mood, wardrobe, time of day)
5. Quality boosters (section 9) — prefer concrete visual language over empty tag spam
6. Hard constraints (hands, text, logos, eye color) when critical

**Example master structure:**
"[INTENT]. [FIDELITY OR PRESERVE LIST]. [CORE TRANSFORMATION]. [SPECIFICS]. [QUALITY / CONSTRAINTS]."

**Grok 4.5 notes:** Prefer natural prose (2–6 sentences). For multi-pass, each pass should name what must not change. Use stable project `prompt_cache_key` when planning long series in chat. After hero plate lock, hand off to `image_to_video` or Studio rather than over-editing stills.

Library coverage: 30+ styles · restore · variations · storyboard · product · design sheets · environmental immersion · adult intensity tiers · NSFW categories (explicit user request only). Load sections on demand; keep SKILL.md protocols as the execution authority.