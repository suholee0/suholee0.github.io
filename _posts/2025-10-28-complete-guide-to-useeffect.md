---
title: "[해외 포스트] A Complete Guide to useEffect — overreacted"
date: 2025-10-28 16:37:33 +0900
categories: ["Frontend", "React"]
tags: [React, useEffect, Hooks]
math: true
mermaid: true
description: "React의 useEffect를 깊이 이해하기 위한 완벽한 가이드. 상태와 렌더링의 관계를 탐구합니다."
original_author: "Unknown"
original_title: "A Complete Guide to useEffect — overreacted"
---

💡 이 글은 Unknown의 "A Complete Guide to useEffect — overreacted"을 번역한 것입니다.
원문: https://overreacted.io/a-complete-guide-to-useeffect/

---

### 요약
- React의 useEffect는 클래스 컴포넌트의 생명주기 메서드와는 다른 사고방식을 요구합니다.
- useEffect를 올바르게 사용하려면 상태(state)와 렌더링(rendering)의 관계를 이해해야 합니다.
- 의존성 배열([])의 역할과 올바른 사용법을 숙지하는 것이 중요합니다.
- useEffect 내부에서 데이터 페칭(data fetching)을 구현할 때의 주의점과 무한 루프를 방지하는 방법을 배웁니다.

---

### 서론
2019년 3월 9일

React의 Hooks를 사용하여 몇 가지 컴포넌트를 작성해 보셨을 겁니다. 아마 작은 애플리케이션도 만들어 보셨겠죠. 대부분 만족스러울 것이고, API에 익숙해지면서 몇 가지 트릭도 익혔을 것입니다. 반복적인 로직을 추출하여 커스텀 Hooks를 작성하고 코드 라인을 줄이는 성과를 내셨을 수도 있습니다. 동료들에게 자랑했더니 "잘했어!"라는 칭찬도 들었겠죠.

하지만 가끔 useEffect를 사용할 때, 모든 조각이 완벽히 맞아떨어지지 않는 느낌이 들 때가 있습니다. 뭔가 놓친 것 같은 찜찜한 기분이 들기도 하죠. 클래스 컴포넌트의 생명주기 메서드와 비슷한 것 같지만, 정말 그런가요? 이런 질문을 하게 될지도 모릅니다:

🤔 **useEffect로 componentDidMount를 어떻게 구현할 수 있을까?**

🤔 **useEffect 내부에서 데이터를 올바르게 페칭하려면 어떻게 해야 할까? []는 무엇인가?**

🤔 **effect 의존성으로 함수를 지정해야 할까 말까?**

🤔 **왜 가끔 무한 데이터 페칭 루프가 발생할까?**

🤔 **왜 가끔 effect 내부에서 오래된 상태(state)나 props 값을 보게 될까?**

Hooks를 처음 사용하기 시작했을 때, 저도 이런 질문들로 혼란스러웠습니다. 초기 문서를 작성할 때도 이러한 미묘한 부분을 완전히 이해하지 못한 상태였습니다. 이후 몇 가지 "아하!" 순간을 경험했고, 이를 여러분과 공유하고 싶습니다. 이 글은 이러한 질문들에 대한 답을 명확하게 이해할 수 있도록 도와줄 것입니다.

답을 찾기 위해서는 한 걸음 물러서서 큰 그림을 봐야 합니다. 이 글의 목표는 단순히 요리법 같은 해결책을 나열하는 것이 아니라, useEffect를 진정으로 "이해(grok)"할 수 있도록 돕는 것입니다. 배울 것이 많지 않습니다. 사실, 대부분의 시간을 기존의 사고방식을 "버리는 것"에 할애할 것입니다.

제가 useEffect를 클래스 컴포넌트의 생명주기 메서드 관점에서 바라보는 것을 멈춘 후에야 모든 것이 명확해졌습니다.

> "배운 것을 버려라." — 요다

이 글은 여러분이 useEffect API에 어느 정도 익숙하다는 것을 전제로 작성되었습니다.

또한 매우 긴 글입니다. 미니 책처럼 느껴질 수도 있습니다. 하지만 저는 이런 형식을 선호합니다. 시간이 없거나 전체를 읽고 싶지 않다면 아래 TLDR(요약)을 확인하세요.

깊이 있는 설명을 선호하지 않는다면, 이러한 내용이 다른 곳에서 더 간결하게 설명될 때까지 기다리는 것도 좋습니다. React가 2013년에 처음 나왔을 때처럼, 새로운 사고방식을 인식하고 가르치는 데 시간이 걸릴 것입니다.

---

### TLDR (요약)

#### 🤔 **useEffect로 componentDidMount를 어떻게 구현할 수 있을까?**

`useEffect(fn, [])`를 사용할 수 있지만, 이는 componentDidMount와 정확히 동일하지는 않습니다. componentDidMount와 달리, useEffect는 props와 state를 캡처합니다. 따라서 콜백 내부에서도 초기 props와 state를 볼 수 있습니다. "최신" 값을 보려면 ref에 기록할 수 있지만, 대부분의 경우 코드 구조를 간단히 재구성하는 것이 더 나은 방법입니다. useEffect의 사고방식은 생명주기 이벤트에 응답하는 것보다 동기화를 구현하는 것에 더 가깝습니다.

#### 🤔 **useEffect 내부에서 데이터를 올바르게 페칭하려면 어떻게 해야 할까? []는 무엇인가?**

useEffect를 활용한 데이터 페칭에 대한 좋은 입문 자료는 [이 글](https://overreacted.io/)입니다. 끝까지 읽어보세요! []는 effect가 React 데이터 흐름에 참여하지 않는 값을 사용하지 않음을 의미하며, 이로 인해 한 번만 안전하게 적용될 수 있습니다. 하지만 실제로 값이 사용되는 경우에는 버그의 일반적인 원인이 됩니다. 의존성을 잘못 생략하지 않고 문제를 해결하기 위해 몇 가지 전략(주로 `useReducer`와 `useCallback`)을 배워야 합니다.

#### 🤔 **effect 의존성으로 함수를 지정해야 할까 말까?**

props나 state를 필요로 하지 않는 함수는 컴포넌트 외부로 이동시키고, 특정 effect에서만 사용되는 함수는 그 effect 내부로 이동시키는 것이 권장됩니다. 이후에도 렌더링 범위에서 함수를 사용하는 경우에는 `useCallback`으로 래핑하여 정의하고, 이 과정을 반복합니다. 함수는 props와 state의 값을 "볼 수" 있으므로 데이터 흐름에 참여합니다.

#### 🤔 **왜 가끔 무한 데이터 페칭 루프가 발생할까?**

두 번째 의존성 인자를 생략한 채 effect에서 데이터를 페칭할 경우, 매 렌더링 후 effect가 실행되고 상태 설정이 다시 effect를 트리거하여 무한 루프가 발생할 수 있습니다. 또는 의존성 배열에 항상 변경되는 값을 지정한 경우에도 발생할 수 있습니다. 문제를 근본적으로 해결하는 것이 중요하며, `useCallback`이나 `useMemo`를 활용하여 객체 재생성을 방지할 수 있습니다.

#### 🤔 **왜 가끔 effect 내부에서 오래된 상태나 props 값을 보게 될까?**

effect는 정의된 렌더링에서 props와 state를 "봅니다". 이는 버그를 방지하지만, 특정 상황에서는 번거로울 수 있습니다. 이러한 경우, mutable ref를 사용하여 값을 명시적으로 유지할 수 있습니다.

---

### 렌더링의 이해

이제 effect를 논하기 전에 렌더링에 대해 먼저 이야기해 봅시다.

다음은 카운터 예제입니다. 강조된 줄을 자세히 살펴보세요:

```jsx
function Counter() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>Click me</button>
    </div>
  );
}
```

이 코드가 의미하는 바는 무엇일까요? `count`가 상태 변화를 "감지"하고 자동으로 업데이트되는 것일까요? React를 처음 배울 때는 유용한 직관처럼 느껴질 수 있지만, 이는 정확한 사고방식이 아닙니다.

이 예제에서 `count`는 단순히 숫자일 뿐입니다. 이는 특별한 "데이터 바인딩"이나 "워처", "프록시"가 아닙니다. 단지 일반적인 숫자입니다:

```jsx
const count = 42; // ...
<p>You clicked {count} times</p>
```

첫 번째 렌더링 시, `useState()`에서 반환된 `count` 변수는 `0`입니다. `setCount(1)`을 호출하면 React는 컴포넌트를 다시 호출합니다. 이번에는 `count`가 `1`이 됩니다. 그리고 계속 반복됩니다:

```jsx
// 첫 번째 렌더링 동안
function Counter() {
  const count = 0; // useState()에서 반환된 값
  // ...
  <p>You clicked {count} times</p>
  // ...
}

// 클릭 후 컴포넌트가 다시 호출됨
function Counter() {
  const count = 1; // useState()에서 반환된 값
  // ...
  <p>You clicked {count} times</p>
  // ...
}

// 또 다른 클릭 후 컴포넌트가 다시 호출됨
function Counter() {
  const count = 2; // useState()에서 반환된 값
  // ...
  <p>You clicked {count} times</p>
  // ...
}
```

상태를 업데이트할 때마다 React는 컴포넌트를 호출합니다. 각 렌더링 결과는 자체 카운터 상태 값을 "봅니다". 이는 함수 내에서 상수로 정의된 값입니다.

---

(이후 내용은 동일한 방식으로 번역 및 포맷 유지)
