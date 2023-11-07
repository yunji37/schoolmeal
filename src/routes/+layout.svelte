<header>
  <div class="navbar">
    <img src="/src/lib/images/logo.png" alt="" />
    <a href="/todaymeal"> 오늘의 급식 </a>
    <a href="/streaming">급식실</a>
    <a href="/">내 정보</a>
  </div>
</header>

<slot />

<!-- 자식 콘텐츠가 부모 콘텐츠의 html을 받아올 수 있음. -->

<style lang="scss">
  .navbar {
    width: 100%;
    background-color: var(--light-blue);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 25px 0;
    height: 5vh;

    img {
      position: relative;
      width: 7rem;
      height: 7rem;
      margin: 100px;
    }

    a {
      position: relative;
      display: flex;
      text-decoration-line: none;
      font-size: 18px;
      color: var(--text-blue);
      margin: 0 100px;

      &::after {
        content: "";
        position: absolute;
        left: 0;
        width: 100%;
        bottom: -6px;
        height: 3px;
        background: var(--purple);
        border-radius: 40px;
        transform: scaleX(0);
        transform-origin: right;
        transition: transform 0.3s;
      }

      &:hover::after {
        transform-origin: left;
        transform: scaleX(1);
      }
    }

    @media (max-width: 800px) {
      height: 3vh;

      img {
        width: 4rem;
        height: 4rem;
        margin: 0;
      }

      a {
        font-size: 12px;
        margin: 0 30px;
      }
    }
  }
</style>
