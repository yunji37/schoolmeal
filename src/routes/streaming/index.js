import { serve } from "@hono/node-server"; // nodejs에서 hono를 사용할 수 있도록 함.
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { cors } from "hono/cors";

const app = new Hono();
app.use(
  // 미들웨어 등록하는 역할
  "/output/*",
  cors({
    // middleware
    origin: ["http://localhost:5173"], // 5500포트에 대한 요청만 받음
  })
);

app.use("/output/*", serveStatic({ root: "./test" }));
app.get("/", (c) => c.text("Hello Node.js!")); // 경로에 대한 GET요청을 처리. (?)
console.log("start");

serve({
  // 서버 시작
  fetch: app.fetch,
  port: 4000,
  hostname: "0.0.0.0",
});

// serverStatic : 정적파일을 제공.
// 정적 파일이란, 서버에서 변경되지 않고 그대로 제공되는 파일을 의미합니다. 예를 들면, image, css 파일, js 파일 등이 있습니다.

// 미들웨어는 클라이언트 요청을 처리하기 전에 실행되는 함수로 요청고 응답에 대한 정보를 변경하거나, 다음 미들웨어를 호출하기 전에 처리할 작업을 수행할 수 있습니다.
// 인자는 두개를 받습니다. 첫번쨰 인자는 선택적으로 경로를 지정할 수 있고, 두번째는 미들웨어 함수를 정의합니다. 경로를 지정하지 않으면 모든 요청에 대해 미들웨어를 실행합니다.
