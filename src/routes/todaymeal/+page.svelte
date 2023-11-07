<script lang="ts">
  import { toasts, ToastContainer, FlatToast } from "svelte-toasts";
  import { auth, db } from "../firebaseInit";
  import { ref, onValue } from "firebase/database";

  let allergies: any;

  // toastr 메시지 위치 수정

  auth.onAuthStateChanged((user) => {
    // 사용자의 로그인 상태의 변화 관찰
    if (user) {
      // 사용자가 로그인 했다면
      // User is signed in.
      const uid = user.uid; // 현재 로그인한 사용자의 고유 식별자 저장

      const dbRefObject = ref(db, `users/${uid}/allergies`); // 사용자의 알레르기 정보 데이터베이스 접근

      onValue(
        // dbRefObject 값에 변화가 생겼을 때 실행
        dbRefObject, // reference
        (snap) => {
          // callback
          allergies = snap.val(); // 데이터베이스에서 가져온 알러지 정보 저장
          console.log("login");
        },
        {
          onlyOnce: true, // 콜백함수가 한 번만 호출되도록 설정
        }
      );
    } else {
      // user 객체가 없을 때 (로그인이 안 돼있을 때)
      console.log("User is signed out");
    }
  });

  const allergenMap = {
    "1": "난류",
    "2": "우유",
    "3": "메밀",
    "4": "땅콩",
    "5": "대두",
    "6": "밀",
    "7": "고등어",
    "8": "게",
    "9": "새우",
    "10": "돼지고기",
    "11": "복숭아",
    "12": "토마토",
    "13": "아황산류",
    "14": "호두",
    "15": "닭고기",
    "16": "쇠고기",
    "17": "오징어",
    "18": "조개류",
    "19": "잣",
  };

  let date = new Date(); // 현재 날짜와 시간

  $: viewYear = date.getFullYear(); // 현재 연도
  $: viewMonth = date.getMonth(); // 현재 월

  let calendarArray: number[] = [];

  const makeCal = (date: Date) => {
    // 인자로 받은 날짜의 달력을 만듬.
    const tempDate = new Date(date); // 새로운 date 객체 생성
    tempDate.setDate(1); // 일자를 1로 설정

    const firstEmpty = tempDate.getDay(); // 해당 월 첫째 날의 요일 정보가 저장

    // 해당월의 마지막 날을 구함.
    tempDate.setMonth(tempDate.getMonth() + 1);
    tempDate.setDate(0);

    // 필요한 빈칸 수 계산
    const last = tempDate.getDate(); // 해당 월의 마지막 날을 저장
    const lastEmpty = 6 - tempDate.getDay(); //  해당 월의 마지막 요일과 토요일 사이에 몇 개의 빈 칸이 필요한지 계산

    calendarArray = [
      ...Array(firstEmpty).fill(0), // 월 첫째주 빈칸 채우기
      ...Array(last)
        .fill(0)
        .map((_, i) => i + 1), // 월의 모든 일자 (인덱스 0 없앰.)
      ...Array(lastEmpty).fill(0), //마지막 주 빈칸 채우기
    ];
  };

  $: makeCal(date); // date값이 변경될 때마다 makeCal 함수 호출

  const prevMonth = () => {
    date = new Date(viewYear, viewMonth - 1);
    selectedDateNum = date.getDate();
    selectedDate = `${date.getFullYear()}년 ${
      date.getMonth() + 1
    }월 ${selectedDateNum}일`;
  };

  const nextMonth = () => {
    date = new Date(viewYear, viewMonth + 1);
    selectedDateNum = date.getDate();
    selectedDate = `${date.getFullYear()}년 ${
      date.getMonth() + 1
    }월 ${selectedDateNum}일`;
  };

  const goToday = () => {
    date = new Date(); // 새로운 date 객체 생성
    viewYear = date.getFullYear();
    viewMonth = date.getMonth();
    selectedDateNum = date.getDate();
    selectedDate = `${viewYear}년 ${viewMonth + 1}월 ${selectedDateNum}일`;

    const paddedMonth = String(date.getMonth() + 1).padStart(2, "0"); // 월을 두자리 수로 변환
    const paddedDay = String(selectedDateNum).padStart(2, "0"); // 일을 두자리 수로 변환
    getMealData(date.getFullYear(), paddedMonth, paddedDay); // 위에서 구한 날짜정보를 사용해 해당 날짜의 식단데이터를 요청
  };

  let selectedDate = "날짜를 선택하세요!"; // 사용자가 달력에서 날짜를 선택했을 때 그 값을 저장 = 초기값
  let mealData: { DDISH_NM: any } | null = null; // 초기값 null

  async function getMealData(year: number, month: string, day: string) {
    const url = `https://open.neis.go.kr/hub/mealServiceDietInfo?Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE=J10&SD_SCHUL_CODE=7781166&MLSV_YMD=${year}${month}${day}`;
    let addedAllergens = new Set(); // set객체 생성후 할당

    try {
      // API에 GET 요청을 보냄
      const response = await fetch(url);
      // 응답이 성공적이지 않은 경우 에러를 발생
      if (!response.ok) {
        throw new Error("error");
      }

      // 응답 내용을 JSON 형태로 파싱
      const data = await response.json();

      // 파싱한 데이터에서 필요한 정보가 있는 경우
      if (data.mealServiceDietInfo && data.mealServiceDietInfo[1]) {
        // 식단 정보를 저장
        mealData = data.mealServiceDietInfo[1].row[0];

        // 식단 정보에서 각각의 음식을 분리하여 배열로 만듬
        let foodsInMeal = mealData.DDISH_NM.split("<br/>");

        for (let food of foodsInMeal) {
          // 각 음식에서 알레르기 번호 부분을 추출합니다.
          let allergenInfo = food.slice(food.lastIndexOf(" (") + 2, -1);

          if (allergenInfo) {
            // 알레르기 번호들을 분리하여 배열로 만듭니다.
            let allergensInFood = allergenInfo.split(".");

            for (let number of allergensInFood) {
              let actualAllergen = allergenMap[number];

              // 번호에 해당하는 알레르기 이름을 찾음
              if (actualAllergen === undefined) {
                console.error(`Undefined allergen: ${number}`);
                continue;
              }

              if (allergies && allergies[actualAllergen]) {
                addedAllergens.add(actualAllergen);
              }
            }
          }
        }

        if (addedAllergens.size > 0) {
          toasts.add({
            title: "알레르기 주의",
            description: `주의! 오늘의 급식에 ${Array.from(addedAllergens).join(
              ", "
            )}(이)가 포함되어 있습니다.`,
            duration: 3500,
            placement: "bottom-right",
            showProgress: true,
            type: "warning",
          });
        }
      } else {
        // 필요한 정보가 없는 경우 대체 텍스트를 사용합니다.
        mealData = { DDISH_NM: "해당하는 데이터가 없습니다." };
      }

      const reg = /[*]/gi;
      const mealTextContainer = document.getElementById("Newline");
      mealTextContainer!.innerHTML = mealData!.DDISH_NM.replace(
        /\n/g,
        "<br>"
      ).replace(reg, "");
    } catch (err) {
      // API 호출이나 데이터 처리 중 에러가 발생한 경우 대체 텍스트를 사용합니다.
      console.error(err);
      mealData = { DDISH_NM: "요청에 실패하였습니다." };
    }
  }

  let selectedDateNum: number | null = null;
  $: {
    if (selectedDateNum !== null) {
      const Month = String(viewMonth + 1).padStart(2, "0");
      const Day = String(selectedDateNum).padStart(2, "0");
      getMealData(viewYear, Month, Day);
    }
  }

  function onDateClick(num: number) {
    if (num !== 0) {
      selectedDate = `${viewYear}년 ${viewMonth + 1}월 ${num}일`;
      selectedDateNum = num;
    }
  }
</script>

<section>
  <ToastContainer let:data>
    <FlatToast {data} />
  </ToastContainer>
  <div class="calendar">
    <div class="header">
      <div class="year-month">{viewYear}년 {viewMonth + 1}월</div>
      <div class="nav">
        <button class="nav-btn" on:click={prevMonth}>&lt;</button>
        <button class="nav-btn go-today" on:click={goToday}>Today</button>
        <button class="nav-btn" on:click={nextMonth}>&gt;</button>
      </div>
    </div>
    <div class="line" />
    <div class="days">
      <div class="day">일</div>
      <div class="day">월</div>
      <div class="day">화</div>
      <div class="day">수</div>
      <div class="day">목</div>
      <div class="day">금</div>
      <div class="day">토</div>
    </div>
    <div class="dates">
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      {#each calendarArray as num}
        <div
          class="date {selectedDateNum === num ? 'selected' : ''}"
          on:click={() => onDateClick(num)}
        >
          <span class="this">{num === 0 ? "" : num}</span>
        </div>
      {/each}
    </div>
  </div>

  <div class="meal">
    <div class="datepic">{selectedDate}</div>
    <div class="line2" />
    <div id="Newline" class="setback meal-tx">
      {mealData ? mealData.DDISH_NM : ""}
    </div>
  </div>
</section>

<style lang="scss">
  * {
    font-family: sans-serif;
    box-sizing: border-box;
  }

  .selected {
    background-color: var(--text-blue) !important;
    color: #c5e1fb;
  }

  section {
    display: flex;
    margin: 3%;
    height: 83vh;

    .calendar {
      width: 80%;
      background-color: #9eb6d6;
      padding: 1rem;
      margin: 1rem;
      border-radius: 1.2rem;

      .line {
        border: 0.07rem solid #ffffff;
        opacity: 30%;
      }

      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem;

        .year-month {
          font-size: 2.25rem;
          color: #ffffff;
        }

        .nav {
          display: flex;
          border: 0.07rem solid #ffffff;
          border-radius: 0.275rem;

          .nav-btn {
            width: 1.5rem;
            height: 1.3rem;
            color: #ffffff;
            border: none;
            font-size: 1rem;
            line-height: 1.8rem;
            background-color: transparent;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
          }

          .go-today {
            width: 4.3rem;
            border-left: 0.07rem solid #ffffff;
            border-right: 0.07rem solid #ffffff;
          }
        }
      }

      .days {
        display: flex;
        justify-content: space-around;
        margin: 1.4rem 0;

        .day {
          text-align: center;
          color: #ffffff;
          opacity: 75%;
        }
      }

      .dates {
        display: flex;
        flex-flow: row wrap;
        height: 32rem;

        .date {
          flex-grow: 1;
          flex-shrink: 0;
          height: 3.7rem;
          background-color: var(--light-blue);
          border-radius: 0.75rem;
          margin-right: 0.3rem;
          padding: 1.26rem;
          font-size: 1.3rem;
          font-weight: bold;
          flex-basis: calc(14.29% - 0.31rem);
          text-align: center;
        }

        .date:nth-child(7n + 1) {
          color: #d13e3e;
        }

        .date:nth-child(7n) {
          color: #396ee2;
        }
      }
    }

    .meal {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      margin-top: 2vw;

      .meal-tx {
        font-size: 2.3rem;
        font-weight: 350;
        color: var(--navy-blue);
      }

      .datepic {
        font-size: 40px;
        color: var(--dark-blue);
      }

      .line2 {
        width: 100%;
        border: 1.5px solid var(--dark-blue);
        margin: 1rem 0 1rem 0;
      }

      .setback {
        width: 37.5rem;
        height: 27rem;
        margin: 0.93rem 0 1.87rem 6.25rem;
        box-shadow: 0px 5px 10px #000000;
        background-color: var(--light-blue);
        border-radius: 0.93rem;
        display: flex;
        justify-content: space-between;
        padding: 2rem;
        overflow: hidden;
      }
    }
  }

  @media (max-width: 768px) {
    section {
      flex-direction: column;
      align-items: center;
      margin: 2%;

      .calendar {
        width: 90%;
        margin: 1rem 0;
        padding: 1rem;

        .header {
          padding: 0.5rem;

          .year-month {
            font-size: 1.5rem;
          }

          .nav .nav-btn {
            width: 1rem;
            height: 1rem;
            font-size: 0.75rem;
            line-height: 1.5rem;
          }

          .nav .go-today {
            width: 3rem;
          }
        }

        .days {
          margin: 1rem 0;
        }

        .dates {
          height: auto;

          .date {
            height: 2.5rem;
            padding: 0.75rem;
            font-size: 0.87rem;
            flex-basis: calc((100% / 8) - 0.2rem);
            width: 0;
            &:nth-last-child(-n + 7) {
              margin-bottom: 1.4vh;
            }
            margin-bottom: 0.2rem;
          }
        }
      }

      .meal {
        width: 90%;
        margin-top: 2%;

        .meal-tx {
          font-size: 1.2rem;
        }

        .datepic {
          font-size: 1.5rem;
        }

        .line2 {
          margin: 0.5rem 0;
        }

        .setback {
          width: 100%;
          height: 15rem;
          margin: 0.5rem 0 1rem;
          padding: 1rem;
        }
      }
    }
  }
</style>
