This article introduces prompt usage tips for Seedream 4.5 and 4.0's text-to-image generation, image editing, reference-based generation and multi-image creation, helping you quickly get started with image creation and turn ideas into image creations.

General Guidelines

Seedream 4.5 and 4.0 support a wide range of tasks such as text-to-image generation, image editing, reference-based generation and multi-image creation. For optimal image creation results, consider the following best practices when crafting prompts:

1.  **Clearly describe the scene using natural language**  
    Use coherent natural language to describe the **subject + action + environment**. If aesthetics matter, include descriptors of **style,** **color,** **lighting,** or **composition**.
    -   Recommended: A girl in a lavish dress walking under a parasol along a tree-lined path, in the style of a Monet oil painting.
    -   Avoid: Girl, umbrella, tree-lined street, oil painting texture.
2.  **Specify application scenario**  
    If you have a specific use case, explicitly state the image **purpose** and **type** in your prompt.
    -   Recommended: Design a logo for a gaming company. The logo features a dog playing with a game controller. The company name "PITBULL" is written on it.
    -   Avoid: An abstract image of a dog holding a controller, and the word PITBULL on it.
3.  **Enhance stylistic rendering**  
    If a particular style is needed, use **precise style keywords** or **reference images** to achieve better results.

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/60e818dd3f234233a84422774b51abfe~tplv-goo7wpa0wc-image.image)

picture book style

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/a0fbf4ea3eaf4ec78c9969223fde10f2~tplv-goo7wpa0wc-image.image)

children's book illustration style

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/835e5c45884d46c9b3563f277af98e0f~tplv-goo7wpa0wc-image.image)

style reference image

4.  **Improve text rendering accuracy**  
    Use **double quotation marks** for the text that needs to appear in the generated image.
    -   Recommended: Generate a poster with the title "Seedream 4.5".
    -   Avoid: Generate a poster titled Seedream 4.5.
5.  **Clearly define image editing goals and fixed elements**  
    Use **concise**, **unambiguous** **instructions** for modifications. Avoid vague pronouns. If other elements should remain unchanged, specify that explicitly.
    -   Recommended: Dress the tallest panda in pink Peking Opera costume and headgear, keeping its pose unchanged.
    -   Avoid: Put that one in pink clothes.

Prompt guide

## Text-to-Image

Use clear and detailed **natural language** to describe the scene. For complex images, describe elements thoroughly to control the output precisely.

> Compared to the older version Seedream 3.0, Seedream 4.5 and 4.0 have a stronger understanding of text prompts, allowing it to generate the expected images with less description, and **the images are no longer washed out**. Therefore, when using Seedream 4.5 and 4.0, using concise and precise prompts is usually better than repeatedly stacking ornate and complex vocabulary.

| 
Input

 | 

Output

 |
| --- | --- |
| 

**【prompt】**A cluttered office desk. On the desk, there is an open laptop with a screen displaying green code.Next to it, a mug with the word "Developer" on it, with steam rising from the top. An open book lies on the desk, with pages showing a Venn diagram illustrating the nesting relationships of three circles in gray, blue, and light green. A sticky note with a mind map drawn on it, organized in a three-level vertical structure. A fountain pen, with the cap lying beside it. Next to the pen is a smartphone, with a new message notification displayed on the screen. In the corner of the desk, there is a small pot of succulent plants. The background is a blurred bookshelf. Sunlight shines from the right side, casting light and shadow on the desk.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/216793277320424a90a06ee992ebd9ff~tplv-goo7wpa0wc-image.image)

 |
| 

**【prompt】**Interior view of an open refrigerator: Top shelf: On the left, there is a carton of milk featuring an illustration of three cows of different sizes grazing on a grassland. On the right, there is an egg holder containing eight eggs. Middle shelf: A plate holds leftover roasted chicken with a small red flag stuck into it. Next to it is a transparent container filled with strawberries, the container is decorated with images of a pineapple, strawberries and oranges. Bottom shelf: The vegetable drawer contains lettuce, carrots and tomatoes. On the door shelves, there are bottles of ketchup and mayonnaise.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/b0ecb3ea9c644cbfa6bc3ecffcdd1ae7~tplv-goo7wpa0wc-image.image)

 |

Seedream 4.5 and 4.0 can transform knowledge and reasoning outcomes into high-density visual content, such as formulas, diagrams, and educational illustrations. When generating such images, we recommend you to use **precise** **technical** **terminology** to ensure accurate representation of the concepts. Additionally, clearly specify the desired visualization format, layout, and style.

| 
Input

 | 

Output

 |
| --- | --- |
| 

**【prompt】**Draw the following system of binary linear equations and the corresponding solution steps on the blackboard: 5x + 2y = 26; 2x -y = 5.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/5542418531b54f068073d9ea7e2cf206~tplv-goo7wpa0wc-image.image)

 |
| 

**【prompt】**Create an infographic showing the causes of inflation. Each cause should be presented independently with an icon.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/1fd2da22c89f4f528a1f0a505ef01e27~tplv-goo7wpa0wc-image.image)

 |

## Image-to-Image

Seedream 4.5 and 4.0 support combining text and images to perform image editing and reference-based generation tasks. Visual cues like **arrows**, **bounding** **boxes** and **doodles** can help designate specific regions within the image.

### Image Editing

Seedream 4.5 and 4.0 support image editing operations such as **addition**, **deletion**, **replacement**, and **modification** through text prompts. It is recommended to use clear and concise language to precisely indicate the target elements for editing and the specific changes required.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/e08a8aa144d441e5932e15717a644eae~tplv-goo7wpa0wc-image.image)

> **\[Addition\]**  
> **prompt：Add matching silver earrings and a necklace** to the girl in the image

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/5affde557c944cabb0e0a35bf011ae24~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/32abecfd1fd84e56b2e95379946783ab~tplv-goo7wpa0wc-image.image)

> **\[Deletion\]**  
> **prompt：Remove** the girl's **hat**.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/96253cbc5d6942ce9c7cb4a5b55c2250~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/9652ed8ee1084b939a9fc39850224b9a~tplv-goo7wpa0wc-image.image)

> **\[Replacement\]**  
> **prompt：Replace the largest bread man with a croissant man**, keeping the action and expression unchanged.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/1281cd9f97154b25bc1266ddf7b1f366~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/17345381bde048f1b03c85f06ced3b7a~tplv-goo7wpa0wc-image.image)

> **\[Modification\]**  
> **prompt：Turn the three robots into transparent crystal**, colored red, yellow and green from left to right. Make the green one run, yellow walk, red stand.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/8cbeeaece36940d0b395311526267432~tplv-goo7wpa0wc-image.image)

 |

When the image content is complex and **difficult to describe accurately using text alone**, visual indicators such as arrows, bounding boxes, or doodles can be used to specify the editing target and its location.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/1da20e56baf64f2e94992b3eaa157cbb~tplv-goo7wpa0wc-image.image)

> **\[Doodle\]**  
> **prompt：**Insert a TV where **the red area is marked** and a sofa where **the blue area is marked**. Keep the original wooden style.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/d08146660f894b0db00d3696b73a3d26~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/69b235500bdd47fe8abf3505c4d3a2cb~tplv-goo7wpa0wc-image.image)

> **\[Bounding** **Box\]**  
> **prompt：**Enlarge the title to **match the red box** and change its style to match the saxophone icon.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/7ff2ba9212934e06af93e54c7f92b02c~tplv-goo7wpa0wc-image.image)

 |

### Reference-Based Generation

Seedream 4.5 and 4.0 support extracting key information from reference images, such as character design, artistic style, and product features, to enable tasks like character creation, style transfer, and product design.

When there are specific features that need to be preserved (e.g., character identity, visual style, product design), you can upload a reference image to ensure the generated result aligns with expectations.

When using reference images, clearly describe:

-   **Reference Target**: Clearly describe the elements to be extracted and retained from the reference image, such as character design, product material from the reference image.
-   **Generated Scene Description**: Provide detailed information about the desired generated content, including scene, layout, and other specifics.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/831a5653f6d04c0e98e59ecf7ec53533~tplv-goo7wpa0wc-image.image)

> **\[Reference Character\]**  
> **prompt：Based on the character in the reference image**, create an anime figure and place it on a desk. Behind it, place a birthday gift box printed with the character's image. Under the box, there is a book. In front of the gift box, add a round plastic base on which the figure stands. Set the scene indoors and make it as realistic as possible. The generated image should match the size of the original image. Position the figure on the left side of the image. The overall style should be consistent with the reference image, maintaining a cinematic photographic feel.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/24c2dd7e60b9466ca9878efdade45bcd~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/134e11b52a344f69b95384366580a7df~tplv-goo7wpa0wc-image.image)

> **\[Reference Style\]**  
> **prompt：Referencing the linear minimalist style of icons**, design 9 application icons for different scenarios, including: music, weather, calendar, camera, chat, map, alarm clock, shopping cart, and notebook, while maintaining a consistent color scheme.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/aea5b230eb4c4bb0980c0c143303f6a5~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/ab24058e799f47148b25bf1d1e170132~tplv-goo7wpa0wc-image.image)

> **\[Reference Virtual Entity\]**  
> **prompt：**Convert **the character in the picture** into a felt wool figure on a small stand, placed on a dark desk.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/9eed566012d14b7abe5abed039a06fe9~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/f6beba8c063f4c718c9e7b443907019d~tplv-goo7wpa0wc-image.image)

> **\[Reference Style\]**  
> **prompt：**Generate four tops in different materials and colors, **based on the clothing style worn by the girl** in the image. Show only the clothing.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/74d10ac9223d4fa0b3dc121fcb44deec~tplv-goo7wpa0wc-image.image)

 |

When converting sketches (like wireframes, floor plans, hand-drawn prototypes) into high-fidelity images, we recommend the following guidelines:

1.  **Provide a clear original image**. If the image contains text description, indicate "Generate based on the text in the image" in the text prompt.
2.  **Clarify the main subject and requirements**, such as a high-fidelity UI interface or a modern living room.
3.  **Explicitly define key consistencies with the reference**, such as ensuring that furniture placement matches the reference image and that the layout follows the prototype.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/40ee854a670a4e8790512881500a10b2~tplv-goo7wpa0wc-image.image)

> **\[Floor Plan\]**  
> **prompt： Based on this floor plan**, generate a photorealistic image of a "modern minimalist furnished living room + open dining area". The room layout and furniture placement should exactly match the reference. Use a Mediterranean color palette, and keep the spatial structure and orientation consistent with the example. The room should appear spacious and three-dimensional (with a sunlit double-height ceiling above the dining area). From front to back, the scene should include: sofa & green plants, television, dining table & chairs, and floor-to-ceiling windows. Do not include any text or hand-drawn edges from the original sketch.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/3c29067cac8e419c9c9360e30a1f2bea~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/ddf2d38a48064f5589bd116591dcc021~tplv-goo7wpa0wc-image.image)

> **\[Hand-Drawn Prototype\]**  
> **prompt：**This is a hand-drawn wireframe of a web-based housing rental platform's detail page. Please render it into a high-fidelity UI interface **according to the textual annotations in the sketch**. Add sample images in the gallery section, and include sample text content in the housing information and reservation information sections.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/46ab4bc54f7140c484044df24bc56c69~tplv-goo7wpa0wc-image.image)

 |

## Multi-Image Input

Seedream 4.5 and 4.0 support multi-image inputs for **composite editing** such as **combination**, **replacement**, or **style transfer**. When using this feature, it's recommended to clearly specify what to reference or edit from each image.  
For example, replace **the character in Image 2** with **the character from Image 1**, and generate the result in **the style of Image 3**.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/c4bdff18908040b7a0d3248b20700825~tplv-goo7wpa0wc-image.image)

> **\[Replacement\]**  
> **prompt：**Replace **the subject in Image 1** with **the subject from Image 2**.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/53a9e700c7364fbfb9676bbbc536bd11~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/54b6a31586be475fb22d79bb34f4f132~tplv-goo7wpa0wc-image.image)

> **\[Combination\]**  
> **prompt：**Dress **the character in Image 1** with **the outfit from Image 2**.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/b2be95beccef461f904747381ca3de99~tplv-goo7wpa0wc-image.image)

 |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/e97caaa8aa2047ae9e8a797b13be5c2b~tplv-goo7wpa0wc-image.image)

> **\[Style Transfer\]**  
> **prompt：**Apply **the style of Image 2** to Image 1.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/b38d0b74cfd642938ae43b20d4ef0497~tplv-goo7wpa0wc-image.image)

 |

## Multi-Image Output

Seedream 4.5 and 4.0 support generating image sequences with **consistent character continuity** and **unified style**, making it suitable for storyboarding, comic creation, and set-based design scenarios that require a cohesive visual identity, such as IP product design or emoji pack creation.  
When generating multiple images, **you can trigger series generation with phrases like "a series", "a set", or by specifying the number of images**.

| 
Input

 | 

Output

 |
| --- | --- |
| 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/e4d6939a73f64cafb9bef358ee0b6452~tplv-goo7wpa0wc-image.image)

> **【prompt】**Refer to this logo, **create a set of visual designs** for an outdoor sports brand named "GREEN". The products include packaging bags, hats, cards, wristbands, cartons, lanyards. The main visual color is green, with a simple and modern style.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/5eddf0309b704151824b8d285b3fe8d1~tplv-goo7wpa0wc-image.image)

 |
| 

**【prompt】**Generate four film storyboard images, corresponding to the following scenes: astronauts repairing a spacecraft in a space station, suddenly encountering an asteroid belt attack, astronauts taking emergency evasive action, and narrowly returning to the spacecraft after being injured.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/0534bec7063348b393d732034fd64879~tplv-goo7wpa0wc-image.image)

 |
| 

**【prompt】**Generate seven mobile phone wallpapers for Monday through Sunday, featuring natural landscapes, with each image labeled with the corresponding date.

 | 

![Image](https://p9-arcosite.byteimg.com/tos-cn-i-goo7wpa0wc/f566a3c2dec0465a8d6d12d7fc269e35~tplv-goo7wpa0wc-image.image)

 |