<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import {
    GoogleAuthProvider,
    onAuthStateChanged,
    signInWithPopup,
    signOut,
  } from "firebase/auth";
  import { writable, get as getStoreValue } from "svelte/store";
  import { ref, set, get } from "firebase/database";
  import { toasts, ToastContainer, FlatToast } from "svelte-toasts";
  import { auth, db } from "./firebaseInit";
  import {
    allergyStore,
    aller,
    allergyStoreDefaultValues,
  } from "./allergyStore";
  import { emojiEnabledStore, switchStateStore } from "./allergyStore";

  // 새로고침할 때 500 error 고치기 => if문이랑 onMount를 이용하여 해결

  const provider = new GoogleAuthProvider(); // 로그인 객체 생성
  const user = writable(null); // user변수에 대한 스토어 초기값 null.
  let isLoggedOut = false;
  $: isLoggedOutClass = isLoggedOut ? "emojiContainer-loggedOut" : "";
  let container;
  let visibilityChangeHandler;
  // 이모지 애니메이션이 활성화되어 있는지 나타냄
  let emojiEnabled;
  emojiEnabledStore.subscribe((value) => {
    emojiEnabled = value;
  });

  // 스위치 상태
  let switchState;
  switchStateStore.subscribe((value) => {
    switchState = value;
  });

  user.subscribe(($user) => {
    // user 변수가 변하면 실행
    if ($user) {
      fetchUserAllergies($user.uid); // user정보 db 저장
    }
  });

  function saveAllergies() {
    // 사용자가 버튼을 클릭하면
    if (getStoreValue(user)) {
      // 현재 로그인한 사용자가 있으면
      set(
        // 데이터 저장
        ref(db, `users/${getStoreValue(user).uid}/allergies`), // 알레르기 정보 위치에
        getStoreValue(allergyStore) // 알레르기 스토어에 있는 값을 저장
      );

      saveUserData(
        getStoreValue(user).uid,
        getStoreValue(user).displayName,
        getStoreValue(user).email,
        getStoreValue(user).photoURL
      ); // user정보 db 저장

      toasts.add({
        // 알러지 저장 알림
        title: "Success",
        description: "알러지가 저장됐습니다!",
        duration: 2000,
        placement: "bottom-right",
        showProgress: true,
        type: "success",
        theme: "dark",
      });
    }
  }

  user.subscribe(($user) => {
    // user 변수가 변하면 실행
    if ($user) {
      saveUserData($user.uid, $user.displayName, $user.email, $user.photoURL); // user정보 db 저장
    }
  });

  async function signIn() {
    try {
      await signInWithPopup(auth, provider); // 팝업 창을 통해 로그인
    } catch (error) {
      console.error("Sign In Error", error);
    }
  }

  async function logOut() {
    try {
      await signOut(auth);
      isLoggedOut = true;
      console.log("Logged out:", isLoggedOut);
    } catch (error) {
      console.error("Sign Out Error", error);
    }
    allergyStore.set(allergyStoreDefaultValues); //  알레르기 정보 초기화
  }

  function toggleAllergy(allergyName: string) {
    // 알레르기 상태 전환
    let currentAllergies = getStoreValue(allergyStore); // allergyStore에 저장된 값 => currentAllergies에 저장
    currentAllergies[allergyName] = !currentAllergies[allergyName]; // 알레르기 상태 전환
    switchStateStore.set(currentAllergies[allergyName]); // 스위치 상태 업데이트
    allergyStore.set(currentAllergies); // 변경된 정보 스토어 저장
  }

  async function fetchUserAllergies(userId: string) {
    const dbRefUserAllergies = ref(db, `users/${userId}/allergies`); // 사용자의 알레르기 정보를 참조 객체 생성
    const snapshotUserAllergieData = await get(dbRefUserAllergies); // 실제 데이터를 가져옴

    if (snapshotUserAllergieData.exists()) {
      let allergiesFromDB: any = snapshotUserAllergieData.val(); // 알레르기 정보를 읽어옴

      aller.forEach((a) => {
        // 알레르기 항목 순회
        // 만약 데이터베이스에서 가져온 사용자의 알레르기 정보가 특정 항목(a)를 포함하고 있지 않다면
        if (!allergiesFromDB.hasOwnProperty(a)) allergiesFromDB[a] = false;
        // 해당 알레르기 항목(a)를 false로 설정(즉, 해당 알레르기 없음으로 표시)
      });

      allergyStore.set(allergiesFromDB);
    }
  }

  async function saveUserData(
    userId: string,
    name: string,
    email: string,
    imageUrl: string
  ) {
    set(ref(db, `users/${userId}`), {
      // 새로운 유저 데이터 생성
      username: name,
      email: email,
      profile_picture: imageUrl,
      allergies: getStoreValue(allergyStore),
    });
  }

  let circles = [];
  // 이모지 애니메이션을 반복하는 데 사용되는 setInterval의 ID
  let intervalId;
  // 애니메이션 속도를 조절하는 변수
  let speedMultiplier = 1;
  // 애니메이션 프레임 요청의 ID
  let animationFrameId;

  const emoji = [
    "🍎",
    "🍅",
    "🍊",
    "🍌",
    "🌽",
    "🥝",
    "🥦",
    "🫐",
    "🍇",
    "🍆",
    "🍚",
    "🍠",
    "🥔",
  ];

  class Circle {
    x: number;
    y: number; // x,y 현재 이모지의 위치
    color: string; // emoji 문자열?
    v: { x: number; y: number }; // 속도 벡터 (x축과 y축 방향으로 얼마나 빠르게 움직일 것인가)
    range: [number, number]; // 움직임 범위를 설정
    element?: HTMLSpanElement; //  DOM 요소를 참조하는 프로퍼티

    constructor(
      x: number, // 이모지의 현재 위치
      y: number,
      c: string, // 이모지 문자열
      v: { x: number; y: number }, // 이모지의 이동 속도 (x축과 y축 방향)
      range: [number, number] // 이모지의 움직임 범위를 설정
    ) {
      this.x = x;
      this.y = y;
      this.color = c;
      this.v = v;
      this.range = range;

      if (typeof window !== "undefined") {
        // 새로운 span 엘리먼트를 생성하고 설정
        let spanElm = document.createElement("span");
        // span 엘리먼트의 스타일 설정
        spanElm.style.opacity = "0";
        spanElm.style.position = "absolute";
        spanElm.innerHTML = c;
        if (window.innerWidth <= 480) {
          // 이모지 크기 조절 (모바일 화면)
          spanElm.style.fontSize = "16px";
        } else {
          // (pc화면)
          spanElm.style.fontSize = "25px";
        }
        // 이모지 컨테이너에 span 엘리먼트 추가
        container.appendChild(spanElm);

        // span 엘리먼트를 this.element에 저장
        this.element = spanElm;
      }
    }

    update() {
      if (typeof window !== "undefined") {
        // 이모지가 화면 밖으로 나가면
        if (this.y > window.innerHeight) {
          // DOM에서 이모지를 제거
          if (this.element && typeof this.element.remove === "function") {
            this.element.remove();
          }

          // circles 배열에서 이모지를 제거
          const index = circles.indexOf(this);
          if (index !== -1) {
            circles.splice(index, 1);
          }
        } else {
          // 이모지의 위치 업데이트
          this.y += this.v.y;
          this.x += this.v.x;

          // 이모지의 스타일 업데이트
          if (this.element && typeof this.element.style === "object") {
            Object.assign(this.element.style, {
              opacity: "1",
              transform: `translate3d(${this.x}px, ${this.y}px ,0px)`,
            });
          }
        }
      }
    }
  }

  function addCircle(delay, color) {
    if (typeof window !== "undefined") {
      // 3초 뒤 새 인스턴스 생성 , circle 배열에 추가
      setTimeout(function () {
        if (circles.length < 100) {
          let speedX;
          let speedY;

          // 화면 크기에 따라 이모지의 이동 속도를 설정
          if (window.innerWidth <= 480) {
            // Small screens
            speedX = -0.1 + Math.random() * 0.2;
            speedY = 0.5 + Math.random();
          } else {
            // Large screens
            speedX = -0.15 + Math.random() * 0.3;
            speedY = 1.2 + Math.random() * 2;
          }

          // 특정 조건에 따라 속도를 조절합니다.
          speedX *= speedMultiplier;
          speedY *= speedMultiplier;

          // 새로운 Circle 인스턴스 생성
          let c = new Circle(
            Math.random() * window.innerWidth,
            -10,
            color,
            { x: speedX, y: speedY },
            [10 - window.innerWidth / 2, window.innerWidth / 2]
          );

          // circles 배열에 새로운 Circle 인스턴스 추가
          circles.push(c);
        }
      }, delay);
    }
  }

  function animate() {
    if (typeof window !== "undefined") {
      for (let i in circles) {
        circles[i].update();
      }
      // 다음 애니메이션 프레임을 요청
      animationFrameId = requestAnimationFrame(animate);
    }
  }

  function createCircles() {
    if (typeof window !== "undefined") {
      for (let i = 0; i < 15; i++) {
        addCircle(i * 150, emoji[Math.floor(Math.random() * emoji.length)]);
      }
    }
  }

  function startEmojiAnimation() {
    if (typeof window !== "undefined") {
      createCircles();
      // 일정한 간격으로 createCircles 함수를 호출
      intervalId = setInterval(createCircles, 3000);
      // 애니메이션 시작
      animationFrameId = requestAnimationFrame(animate);
    }
  }

  function stopEmojiAnimation() {
    if (typeof window !== "undefined") {
      // setInterval을 멈춤
      if (intervalId) clearInterval(intervalId);
      // 애니메이션을 멈춤
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
      // 모든 Circle 인스턴스를 제거
      circles.forEach((circle) => circle.element?.remove());
      // circles 배열을 비움
      circles = [];
    }
  }

  // 이모지 애니메이션을 켜거나 끄는 함수
  function toggleEmoji() {
    emojiEnabled = !emojiEnabled;
    emojiEnabledStore.set(emojiEnabled);

    if (emojiEnabled) {
      startEmojiAnimation();
    } else {
      stopEmojiAnimation();
    }
  }

  onMount(async () => {
    switchStateStore.set(getStoreValue(switchStateStore) === true);
    onAuthStateChanged(auth, (currentUser) => {
      // 사용자 상태 변화 감지
      user.set(currentUser); // user스토어에 유저 정보 저장
      isLoggedOut = !currentUser; // 로그아웃 상태 업데이트
      if (currentUser) {
        // 로그인한 사용자가 있다면
        fetchUserAllergies(currentUser.uid); // db에서 알레르기 정보 불러오기
      }
      //  else {
      //   allergyStore.set(allergyStoreDefaultValues); // 알레르기 정보 초기화
      // }
    });

    const savedState = getStoreValue(switchStateStore);
    if (savedState !== null) {
      switchState = savedState === true;
    }

    if (typeof window !== "undefined" && typeof document !== "undefined") {
      container = document.getElementById("emojiContainer");
      // 이모지 애니메이션이 활성화되어 있으면 애니메이션을 시작
      if (emojiEnabled) {
        startEmojiAnimation();
      }
      visibilityChangeHandler = () => {
        if (document.visibilityState === "visible") {
          if (emojiEnabled) {
            startEmojiAnimation();
          }
        } else {
          stopEmojiAnimation();
        }
      };
      document.addEventListener("visibilitychange", visibilityChangeHandler);
    }
  });

  onDestroy(() => {
    if (typeof window !== "undefined" && typeof document !== "undefined") {
      stopEmojiAnimation();
      document.removeEventListener("visibilitychange", visibilityChangeHandler);
    }
  });
</script>

<section>
  <div
    id="emojiContainer"
    class:emojiContainer-loggedOut={isLoggedOut}
    bind:this={container}
  />
  <ToastContainer let:data>
    <FlatToast {data} />
  </ToastContainer>

  {#if $user}
    <!-- 로그인한 사용자가 있는 경우 -->
    <div class="container1">
      <div class="info">
        <div class="text_container">
          <div id="whenSignedIn">
            <img class="profil" src={$user.photoURL} alt="User Avatar" />
            <div class="a">
              <div class="welcome_tx">
                안녕하세요<br />{$user.displayName}!
              </div>
              <button id="signOutBtn" on:click={logOut} class="authButton"
                >로그아웃</button
              >
              <button on:click={toggleEmoji} class="toggleEmoji">
                {emojiEnabled ? "이모지 on" : "이모지 off"}
              </button>
            </div>
          </div>
        </div>
        <div class="info_line" />
      </div>
    </div>

    <div class="container2">
      <div class="menu-item">
        <h2 class="menu-text">알레르기 정보 변경하기</h2>
        <div class="set-back">
          <div class="column">
            {#each aller.slice(0, 10) as v, i}
              <label class="switch-container">
                <span class="switch-tx">{i + 1}. {v}</span>
                <input
                  type="checkbox"
                  bind:checked={$allergyStore[v]}
                  on:click={() => toggleAllergy(v)}
                />
              </label>
            {/each}
          </div>
          <div class="column">
            {#each aller.slice(10) as v, i}
              <label class="switch-container">
                <span class="switch-tx">{i + 11}. {v}</span>
                <input
                  type="checkbox"
                  bind:checked={$allergyStore[v]}
                  on:click={() => toggleAllergy(v)}
                />
              </label>
            {/each}
            <button class="allergy_bt" on:click={saveAllergies}
              >Save Allergies</button
            >
          </div>
        </div>
      </div>
    </div>
  {:else}
    <div class="main">
      <!-- 로그인하지 않은 사용자 경우 -->
      <button id="signInBtn" on:click={signIn} class="authButton"
        >구글 로그인</button
      >
      <div class="main_tx">로그인을 하면 알러지기능을 사용할 수 있습니다</div>
    </div>
  {/if}
</section>

<style lang="scss">
  section {
    margin: 0 2%;
    height: 91vh;
    display: flex;
    position: relative;
    flex-direction: row;
    justify-content: center;
    overflow: hidden;

    @media (max-width: 769px) {
      flex-direction: column;
      align-items: flex-start;
    }
  }

  #emojiContainer {
    position: absolute;
    width: 50%;
    height: 100%;
    z-index: -1;
  }

  .emojiContainer-loggedOut {
    width: 100% !important;
  }

  .main {
    display: flex;
    margin: auto;
    @media (max-width: 769px) {
      flex-direction: column;
      align-items: center;
    }

    .main_tx {
      font-size: 2rem;
      background-color: white;
      border-radius: 1rem;
      @media (max-width: 769px) {
        font-size: 1.2rem;
      }
    }

    #signInBtn {
      width: 10rem;
      height: 3rem;
      font-size: 1.3rem;
      background-color: var(--dark-blue);
      color: white;
      padding: auto;
      margin: 0 2rem;
      border-radius: 5px;
      border: none;
      cursor: pointer;

      &:hover {
        background-color: var(--purple);
        color: white;
      }

      @media (max-width: 769px) {
        width: 8rem;
        height: 2rem;
        margin: 2rem;
        font-size: 1rem;
      }
    }
  }

  .container1 {
    width: 50%;

    @media (min-width: 769px) {
      width: 100%;
    }

    .info {
      display: flex;
      flex-direction: row;

      @media (max-width: 768px) {
        width: 24rem;
        flex-wrap: wrap;
        justify-content: start;
      }

      .info_line {
        width: 0.1875rem;
        height: 91vh;
        background-color: var(--dark-blue);
        margin: 0 3.5rem;

        @media (max-width: 768px) {
          width: 100%;
          height: 0.1875rem;
          margin: 1rem auto;
        }
      }

      .text_container {
        display: flex;
        justify-content: center;

        @media (max-width: 768px) {
          justify-content: space-between;
          align-items: center;
        }

        #whenSignedIn {
          display: flex;
          flex-direction: column;

          @media (max-width: 768px) {
            flex-direction: row;
          }

          .profil {
            width: 11.25rem;
            height: 11.25rem;
            margin: 5rem 0 10rem 0;
            display: block;
            margin-left: auto;
            margin-right: auto;
            border-radius: 100px;

            @media (max-width: 768px) {
              width: 7.5rem;
              height: 7.5rem;
              margin: 0;
              margin-right: 7.5rem;
            }
          }

          .a {
            display: flex;
            flex-direction: column;
            text-align: center;

            @media (max-width: 768px) {
              padding: 1.3rem;
            }

            .welcome_tx {
              font-size: 1.5rem;
              text-align: center;

              @media (max-width: 768px) {
                font-size: 1rem;
              }
            }

            .authButton {
              margin: 1.5rem 5rem;
              padding: 0.45rem;
              width: 8rem;
              color: white;
              font-size: 1.3rem;
              background-color: var(--dark-blue);
              border-radius: 5px;
              border: none;
              cursor: pointer;

              @media (max-width: 768px) {
                margin: 0.7rem 0.3rem;
                padding: 0.45rem;
                width: 6rem;
                height: 2rem;
                font-size: 0.8rem;
              }
            }

            .toggleEmoji {
              display: block;
              margin: auto;
              padding: 0.8rem 1.7rem;
              width: fit-content;
              font-size: 1rem;
              background-color: var(--purple);
              border-radius: 25px;
              border: none;
              color: white;
              transition: background-color 0.3s ease-in-out;

              &:hover {
                background-color: var(--dark-blue);
              }
              @media (max-width: 768px) {
                font-size: 0.8rem;
                padding: 0.5rem 1.4rem;
              }
            }
          }
        }
      }
    }
  }

  .container2 {
    display: flex;
    align-items: center;
    margin-right: 7%;

    @media (max-width: 768px) {
      margin: 1.25rem;
      width: 100%;
    }

    .menu-item {
      display: flex;
      flex-direction: column;
      margin-top: -3.5rem;

      .menu-text {
        font-size: 1.7rem;
        margin: 1rem 0;

        @media (max-width: 768px) {
          font-size: 1.3rem;
          margin: 3rem 0 1rem 0;
        }
      }

      .set-back {
        width: 36.5rem;
        height: 26.25rem;
        display: flex;
        margin: 2.5rem 0 0 6.5rem;
        box-shadow: 0px 5px 10px #000000;
        background-color: var(--light-blue);
        border-radius: 0.9375rem;
        justify-content: space-between;
        padding: 1.5625rem;
        overflow: hidden;

        @media (max-width: 768px) {
          width: 19rem;
          height: 26rem;
          margin: 0;
          padding: 0.9375rem;
          flex-direction: column;
          align-items: center;
          overflow: scroll;
        }

        .column {
          display: flex;
          flex-direction: column;

          .switch-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 13.75rem;
            margin-bottom: 0.625rem;
            cursor: pointer;

            .switch-tx {
              font-size: 1.25rem;
              margin: 0.25rem;
            }

            [type="checkbox"] {
              appearance: none;
              position: relative;
              border: max(2px, 0.1em) solid gray;
              border-radius: 1.25em;
              width: 2.3em;
              height: 1.3em;
            }

            [type="checkbox"]::before {
              content: "";
              position: absolute;
              left: 0;
              width: 1em;
              height: 1em;
              border-radius: 50%;
              transform: scale(0.8);
              background-color: gray;
              transition: left 250ms linear;
            }

            [type="checkbox"]:checked {
              background-color: var(--purple);
              border-color: var(--purple);
            }

            [type="checkbox"]:checked::before {
              background-color: white;
              left: 1em;
            }

            [type="checkbox"]:enabled:hover {
              box-shadow: 0 0 0 max(4px, 0.2em) lightgray;
            }
          }
        }

        .allergy_bt {
          width: 10rem;
          height: 3.3rem;
          margin: 0.25rem;
          border-radius: 0.8rem;
          color: beige;
          background-color: var(--dark-blue);
          align-self: center;

          @media (max-width: 768px) {
            width: 100%;
            height: 2.5rem;
          }
        }
      }
    }
  }
</style>
