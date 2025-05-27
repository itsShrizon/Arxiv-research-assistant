
---

## 🎥 Demo Video

See `arxiv-mcp-server` in action! This short video provides a walkthrough of the main features and functionalities.

[![Watch the Demo Video](https://img.youtube.com/vi/YOUR_YOUTUBE_VIDEO_ID/hqdefault.jpg)](https://drive.google.com/file/d/18LjlpyrIzt175p8UOAc_b3oD1BxTZja0/view?usp=sharing)

> **Note:** The image above is a placeholder. Click the image to open the Google Drive video link in a new tab. For a better preview, consider uploading to YouTube and using a proper YouTube thumbnail URL.

---

## 🛠️ Customization

`arxiv-mcp-server` is designed to be easily configurable:

*   **LLM API Keys**: Add your preferred LLM API keys (e.g., OpenAI, Google Gemini) by modifying `src/arxiv_mcp_server/config.py`. It's recommended to use environment variables for sensitive keys.
*   **Paper Storage**: Downloaded papers are stored in `data/papers/` by default. You can configure this path in `config.py` if needed.
*   **LLM Prompts**: Customize the analysis behavior of the LLMs by editing the prompt templates located in `src/arxiv_mcp_server/prompts/`.

---

## 🤝 Contributing

We welcome contributions! If you have ideas for new features, bug fixes, or improvements, please feel free to open an issue or submit a pull request.

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
