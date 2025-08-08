import express from "express";
import session from "express-session";
import bodyParser from "body-parser";
import path from "path";
import { fileURLToPath } from "url";
import { OpenAI } from "openai";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(session({
  secret: "replace-this-secret",
  resave: false,
  saveUninitialized: true,
}));
app.use(express.static(path.join(__dirname, "public")));

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message || "";
  req.session.history = req.session.history || [];
  req.session.history.push({ role: "user", content: userMessage });

  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.setHeader("Transfer-Encoding", "chunked");

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: req.session.history,
      stream: true,
    });

    let assistantText = "";
    for await (const part of completion) {
      const content = part.choices[0]?.delta?.content || "";
      assistantText += content;
      res.write(content);
    }

    req.session.history.push({ role: "assistant", content: assistantText });
    res.end();
  } catch (err) {
    console.error(err);
    res.status(500).end("Error");
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
