<script>
  import { onMount } from "svelte";
  import Hls from "hls.js";

  let video;

  onMount(() => {
    // 컴포넌트가 처음 만들어졌을 때
    const videoSrc = "http://localhost:4000/output/output.m3u8";

    if (Hls.isSupported()) {
      // hls.js를 사용 (hls 사용x)
      let hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
    }
  });
</script>

<section>
  <!-- svelte-ignore a11y-media-has-caption -->
  <video bind:this={video} class="a" id="video" controls />
</section>

<style lang="scss">
  section {
    display: flex;
    justify-content: center;
    margin: 2%;

    @media (max-width: 769px) {
      margin-top: 20%;
    }

    .a {
      width: 70%;
      height: 40rem;

      @media (max-width: 769px) {
        width: 95%;
        height: 20rem;
      }
    }
  }
</style>
