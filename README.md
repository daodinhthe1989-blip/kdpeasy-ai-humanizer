# 🎨 KDPEasy AI Humanizer

A free VIP gift tool from KDPEasy Studio.

Takes any AI-generated image (ChatGPT, Midjourney, DALL-E,
Leonardo, Stable Diffusion) and adds the tiny imperfections that
make it read as handcrafted — grain, paper texture, warmth, colour
grading, subtle vignette. Batch mode processes covers AND interior
images together so the whole book stays visually consistent.

**Live app:** https://kdpeasy-ai-humanizer.streamlit.app

---

## 🇻🇳 Hướng dẫn deploy (dành cho anh chủ tool)

### Bước 1 — Tạo repo mới trên GitHub
1. Mở https://github.com/new
2. **Repository name:** `kdpeasy-ai-humanizer`
3. **Public** ✅
4. ✅ Tick "Add a README file"
5. Bấm **Create repository**

### Bước 2 — Upload 4 file vào repo
Trong repo vừa tạo, bấm **Add file → Upload files**, kéo cả 4 file
trong thư mục `C:\Users\Admin\Downloads\KDPEasy-AI-Humanizer\`:

- `app.py`
- `requirements.txt`
- `runtime.txt`
- `README.md`

Bấm **Commit changes**.

### Bước 3 — Deploy lên Streamlit Cloud
1. Mở https://share.streamlit.io
2. Bấm **Create app → Deploy a public app from GitHub**
3. **Repository:** `daodinhthe1989-blip/kdpeasy-ai-humanizer`
4. **Branch:** `main`
5. **Main file path:** `app.py`
6. **App URL:** `kdpeasy-ai-humanizer`
7. Bấm **Deploy**

Đợi ~2 phút. Mật khẩu vào tool: **`KDPGIFT2026`**

> ⚠️ Lần đầu deploy sẽ mất thêm ~1 phút để install numpy.
> Sau đó chạy nhanh.

---

## 🇺🇸 How customers use it

### What it does
Amazon buyers are getting sharper at spotting AI-generated
covers. "Too smooth", "too digital", "too plastic" are common
1-star review keywords in 2026.

This tool applies a subtle handcrafted layer to any AI image:
grain, paper texture, warmth, colour grading. The image still
looks like the AI-generated art you started with — just less
"AI perfect" and more "book you'd actually buy".

### Why batch mode matters
The killer feature: same style applied to cover AND all
interior illustrations at once. If you only humanize the cover,
the interior pages look inconsistent and readers notice. Batch
mode keeps your whole book visually coherent.

### Step-by-step
1. **Unlock** with the VIP password from your welcome email.
2. **Pick a preset** in the sidebar:
   - **Watercolor Storybook** — soft, paper-textured, gentle
   - **Vintage Warm** — golden-age storybook feel, sepia hint
   - **Handcrafted Illustration** — universal, works for anything
   - **Pastel Drawing** — muted, chalk-on-paper, dreamy
3. **Adjust intensity** (0.3 to 1.6) if you want stronger or lighter
4. **Open advanced sliders** to fine-tune warmth, grain, texture
5. **Upload up to 30 images** — cover + interior all together
6. **Watch the live preview** on the first image
7. **Click "Humanize & download ZIP"** — every image gets the same
   style treatment
8. **Download** and use in your KDP book, Etsy listing, or wherever

### Use cases
- 📚 **Picture book covers + interiors** — consistent look across
  all 14-30 pages
- 🎨 **Coloring book covers** — subtle handcrafted texture
- 🖼️ **Etsy printables** — buyers care about "handmade" feel
- 📖 **Kindle book covers** — pass the "AI look" gut check
- 🎁 **Marketing images** — social media, ads, sales pages

### Pro tips
- Start with **Handcrafted Illustration** preset — safest default
- If it feels too subtle, bump **Overall intensity** to 1.3-1.5
- If it feels too strong, drop intensity to 0.5-0.7
- The same style + slider values are applied to every image —
  that's what gives your book consistency
- Original AI images should be at least 1024×1024 for best results

---

## 🛠️ Tech stack
- **Streamlit** — UI
- **Pillow** — image handling (colour, blend, filters)
- **numpy** — grain, texture generation, vignette

No paid APIs. Runs free on Streamlit Cloud.

---

Made with ❤️ by **KDPEasy Studio** as a thank-you to our VIP list.
