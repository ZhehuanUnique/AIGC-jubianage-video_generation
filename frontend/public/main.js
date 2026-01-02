/**
 * 丝滑 marquee：无缝循环横向滚动 + hover 缓动减速到停 + 离开缓动恢复
 * - 使用 requestAnimationFrame
 * - 使用时间常数的指数平滑（与帧率无关）
 * - transform: translate3d 启用 GPU 合成
 */

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function expSmoothingAlpha(dt, smoothness) {
  // smoothness: 1/s，越大越快接近目标（与帧率无关）
  const k = Math.max(0, smoothness);
  return 1 - Math.exp(-k * dt);
}

function springStep(state, target, dt, freqHz, damping) {
  // 速度弹簧（2D）：让数值接近 target 的同时更"自然"
  // state: { x, v } 这里我们用来控制 speed（x=当前 speed, v=加速度积分出来的速度变化率）
  const f = Math.max(0.001, freqHz);
  const z = clamp(damping, 0.05, 2.0);
  const w = 2 * Math.PI * f;

  const x = state.x;
  const v = state.v;
  const dx = x - target;

  // 经典二阶系统：x'' + 2ζω x' + ω^2 x = ω^2 target
  const a = -2 * z * w * v - (w * w) * dx;
  const v2 = v + a * dt;
  const x2 = x + v2 * dt;
  state.x = x2;
  state.v = v2;
  return state;
}

function setupMarquee(root) {
  const track = root.querySelector("[data-marquee-track]");
  if (!track) return;

  // 参数（你可以按需求调）：
  const baseSpeedPxPerSec = 150; // 初始速度（px/s）
  const hoverStopSeconds = 0.55; // 暂停到停的大致时间感
  const resumeSeconds = 0.65; // 离开恢复到初速的大致时间感
  // 弹簧参数：频率越高越"跟手"，阻尼越大越不回弹
  const speedSpringHz = 3.0;
  const speedDamping = 1.05; // 1 接近接近临界阻尼

  const prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // 无缝循环：复制一份内容，确保任何时候容器都被完全覆盖
  // 复制后宽度 = 原宽度 * 2，确保满屏（只复制一次，避免重复过多）
  // 完全禁用复制，避免重复显示
  // const originalHTML = track.innerHTML;
  // track.insertAdjacentHTML("beforeend", originalHTML);

  let running = true;
  let targetSpeed = prefersReduced ? 0 : baseSpeedPxPerSec;
  const speedState = { x: targetSpeed, v: 0 }; // x=speed, v=speed derivative
  let translateX = 0; // 当前 translateX 值（直接控制位置）
  let lastT = performance.now();

  function measureHalfWidth() {
    // track.scrollWidth 是两份内容的总宽度，一份宽度 = 总宽度 / 2
    // 不使用 Math.floor，保持原始精度，避免精度损失导致的不一致
    // 不再复制，直接使用原始宽度
    const width = track.scrollWidth;
    // 确保宽度至少大于 0
    return width > 0 ? width : 1;
  }

  function measureContainerWidth() {
    // 获取容器（marquee）的宽度，现在容器宽度为浏览器窗口宽度
    // 保持原始精度，避免精度损失
    const width = root.getBoundingClientRect().width;
    // 确保宽度至少大于 0
    return width > 0 ? width : window.innerWidth;
  }

  let halfWidth = 0;
  let containerWidth = 0;

  // 初始化测量（等一帧，确保布局稳定）
  requestAnimationFrame(() => {
    halfWidth = measureHalfWidth();
    containerWidth = measureContainerWidth();
    // 初始位置：确保容器被完全覆盖
    // 由于有两份内容，初始时让第一份内容在容器内，确保满屏
    if (halfWidth > 0 && containerWidth > 0) {
      // 初始 translateX = -halfWidth，这样第一份内容的最后一张卡片在容器左侧边缘
      // 第二份内容会覆盖整个容器，确保满屏
      translateX = -halfWidth;
      track.style.transform = `translate3d(${translateX}px, 0, 0)`;
    }
  });

  // 监听窗口大小变化，更新容器宽度
  const handleResize = () => {
    const oldHalfWidth = halfWidth;
    halfWidth = measureHalfWidth();
    containerWidth = measureContainerWidth();
    // 重新对齐：保持相对位置，确保满屏
    if (oldHalfWidth > 0 && halfWidth > 0) {
      // 计算当前的相对位置（在 [-halfWidth, 0] 范围内）
      let relativeX = translateX;
      while (relativeX < -oldHalfWidth) {
        relativeX += oldHalfWidth;
      }
      while (relativeX > 0) {
        relativeX -= oldHalfWidth;
      }
      // 调整 translateX 保持相对位置比例
      translateX = (relativeX / oldHalfWidth) * halfWidth;
      // 应用变换
      track.style.transform = `translate3d(${translateX}px, 0, 0)`;
    }
  };
  window.addEventListener("resize", handleResize, { passive: true });

  // 拖拽/触摸：手动控制 x，并注入一个短暂的"手势速度"，随后回归自动速度
  let isDragging = false;
  let pointerId = null;
  let lastPointerX = 0;
  let lastPointerT = 0;
  let gestureSpeed = 0; // px/s，正数表示向右拖（内容向右移）

  function updatePosition(deltaX) {
    // 无缝循环逻辑（确保任何时候都满屏，且完全无缝无跳转）
    // 内容有三份，每份宽度 halfWidth
    // 关键：translateX 持续变化（可以是任意值），使用模运算计算实际位置
    // 这样就不会有跳转，看起来就像内容真的无穷无尽一样
    
    if (halfWidth <= 0 || containerWidth <= 0) return;
    
    // translateX 持续减小（内容向左移），可以是任意值（包括很大的负数）
    translateX -= deltaX;
    
    // 使用模运算计算相对位置，确保无缝循环，无跳转
    // relativeX 应该在 [-halfWidth, 0) 范围内循环
    let relativeX = translateX;
    
    // 将 translateX 映射到 [-halfWidth, 0) 范围内
    // 使用模运算确保无缝循环
    relativeX = relativeX % halfWidth;
    // 确保结果在 [-halfWidth, 0) 范围内
    if (relativeX >= 0) {
      relativeX -= halfWidth;
    }
    
    // 应用变换（使用 relativeX 而不是 translateX，确保无缝）
    track.style.transform = `translate3d(${relativeX}px, 0, 0)`;
    
    // 定期重置 translateX 防止数值过大（但不影响视觉效果，因为使用的是 relativeX）
    if (Math.abs(translateX) > halfWidth * 1000) {
      translateX = relativeX;
    }
  }

  function tick(now) {
    if (!running) return;
    const dt = clamp((now - lastT) / 1000, 0, 0.05);
    lastT = now;

    // 实时更新容器宽度（应对窗口大小变化）
    containerWidth = measureContainerWidth();

    // 手势速度会指数衰减回 0（让拖拽放开后自然回归自动滚动）
    const gestureAlpha = expSmoothingAlpha(dt, 10.5);
    gestureSpeed += (0 - gestureSpeed) * gestureAlpha;

    // 用二阶弹簧让速度接近目标：比单纯 lerp 更自然
    springStep(speedState, targetSpeed, dt, speedSpringHz, speedDamping);
    const autoSpeed = speedState.x;

    if (!prefersReduced) {
      if (!isDragging) {
        // 从右到左移动：内容从右侧进入，向左侧移动
        // 计算每帧的移动距离
        const deltaX = (autoSpeed - gestureSpeed) * dt;
        updatePosition(deltaX);
      }
    }

    requestAnimationFrame(tick);
  }

  requestAnimationFrame(tick);

  // hover：减速到停，离开恢复
  const onEnter = () => {
    targetSpeed = 0;
    // 通过"预设速度导数"让停下更像渐进刹车
    speedState.v *= 0.25;
  };
  const onLeave = () => {
    targetSpeed = prefersReduced ? 0 : baseSpeedPxPerSec;
    speedState.v *= 0.25;
  };

  root.addEventListener("mouseenter", onEnter, { passive: true });
  root.addEventListener("mouseleave", onLeave, { passive: true });

  // 交互：拖拽/触摸拖动（不抢滚动条，水平拖动为主）
  root.addEventListener("pointerdown", (e) => {
    if (prefersReduced) return;
    if (e.button !== undefined && e.button !== 0) return;
    isDragging = true;
    pointerId = e.pointerId;
    root.setPointerCapture(pointerId);
    root.classList.add("is-dragging");
    lastPointerX = e.clientX;
    lastPointerT = performance.now();
    gestureSpeed = 0;
    // 拖动时把自动目标速度降一点，避免"抢回去"的感觉
    targetSpeed = 0;
  });

  root.addEventListener("pointermove", (e) => {
    if (!isDragging || e.pointerId !== pointerId) return;
    const now = performance.now();
    const dx = e.clientX - lastPointerX;
    const dt = clamp((now - lastPointerT) / 1000, 0.001, 0.05);
    lastPointerX = e.clientX;
    lastPointerT = now;

    // 拖拽：手向右拖应让内容向右（translateX 增加），手向左拖应让内容向左（translateX 减小）
    translateX += dx;
    
    // 使用与 updatePosition 相同的模运算逻辑，确保无缝无跳转
    if (halfWidth > 0 && containerWidth > 0) {
      let relativeX = translateX % halfWidth;
      // 确保结果在 [-halfWidth, 0) 范围内
      if (relativeX >= 0) {
        relativeX -= halfWidth;
      }
      track.style.transform = `translate3d(${relativeX}px, 0, 0)`;
    } else {
      track.style.transform = `translate3d(${translateX}px, 0, 0)`;
    }

    // 估计手势速度（px/s），用于放开后的惯性
    const inst = dx / dt; // px/s，右为正
    // 低通一下，减少手抖
    gestureSpeed = gestureSpeed * 0.6 + inst * 0.4;
  });

  function endDrag() {
    if (!isDragging) return;
    isDragging = false;
    root.classList.remove("is-dragging");
    try {
      if (pointerId != null) root.releasePointerCapture(pointerId);
    } catch {}
    pointerId = null;
    // 放开后恢复自动目标速度，并把"手势速度"带进去（会在 tick 里衰减）
    targetSpeed = prefersReduced ? 0 : baseSpeedPxPerSec;
    speedState.v *= 0.35;
  }

  root.addEventListener("pointerup", endDrag);
  root.addEventListener("pointercancel", endDrag);
  root.addEventListener("lostpointercapture", endDrag);

  // 页面不可见时暂停（省电更稳）
  const onVis = () => {
    if (document.hidden) {
      running = false;
    } else {
      running = true;
      lastT = performance.now();
      requestAnimationFrame(tick);
    }
  };
  document.addEventListener("visibilitychange", onVis, { passive: true });

  // 失焦时也停一下，回到页面再恢复（体验更像"丝滑播放器"）
  const onBlur = () => {
    targetSpeed = 0;
  };
  const onFocus = () => {
    if (!isDragging) targetSpeed = prefersReduced ? 0 : baseSpeedPxPerSec;
  };
  window.addEventListener("blur", onBlur, { passive: true });
  window.addEventListener("focus", onFocus, { passive: true });

  return () => {
    document.removeEventListener("visibilitychange", onVis);
    window.removeEventListener("blur", onBlur);
    window.removeEventListener("focus", onFocus);
    window.removeEventListener("resize", handleResize);
    root.removeEventListener("mouseenter", onEnter);
    root.removeEventListener("mouseleave", onLeave);
    running = false;
  };
}

// 背景视频处理：确保视频正确加载和循环播放
function setupBackgroundVideo() {
  const video = document.querySelector(".bg-video");
  if (!video) return;

  // 确保视频循环播放
  video.addEventListener("loadeddata", () => {
    video.play().catch((err) => {
      console.warn("视频自动播放失败:", err);
    });
  });

  // 视频结束时重新播放（确保无缝循环）
  video.addEventListener("ended", () => {
    video.currentTime = 0;
    video.play().catch((err) => {
      console.warn("视频循环播放失败:", err);
    });
  });

  // 处理视频加载错误
  video.addEventListener("error", () => {
    console.warn("背景视频加载失败，将使用备用背景");
    // 可以在这里添加备用背景图
  });

  // 确保视频在页面可见时播放
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      video.play().catch((err) => {
        console.warn("视频恢复播放失败:", err);
      });
    }
  });
}

document.addEventListener(
  "DOMContentLoaded",
  () => {
    // 设置背景视频
    setupBackgroundVideo();
    // 设置流动播放
    document.querySelectorAll("[data-marquee]").forEach((el) => setupMarquee(el));
  },
  { passive: true }
);
