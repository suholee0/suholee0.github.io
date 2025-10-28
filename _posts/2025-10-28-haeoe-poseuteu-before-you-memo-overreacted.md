---
title: "[해외 포스트] Before You memo() — overreacted"
date: 2025-10-28 16:29:28 +0900
categories: ["Frontend", "React"]
tags: [React, 성능 최적화, memo, useMemo]
math: true
mermaid: true
description: "React 성능 최적화를 위한 memo()와 useMemo() 사용 전 고려할 점에 대한 설명"
---

> 💡 이 글은 Unknown의 "Before You memo() — overreacted"을 번역한 것입니다.
> 원문: https://overreacted.io/before-you-memo/

## 요약
- React 성능 최적화 방법
- 상태 관리 위치의 중요성
- memo()와 useMemo() 사용 전 고려할 점

2021년 2월 23일

React 성능 최적화에 관한 많은 글들이 있습니다. 일반적으로 상태 업데이트가 느린 경우, 다음을 확인해야 합니다:

- 프로덕션 빌드를 실행 중인지 확인하세요. (개발 빌드는 의도적으로 느리며, 극단적인 경우에는 10배까지 느릴 수 있습니다.)
- 상태를 필요 이상으로 트리의 상위에 두지 않았는지 확인하세요. (예를 들어, 입력 상태를 중앙 집중식 저장소에 두는 것이 최선의 방법이 아닐 수 있습니다.)
- React DevTools Profiler를 실행하여 무엇이 다시 렌더링되는지 확인하고, 가장 비용이 많이 드는 서브트리를 memo()로 감싸세요. (그리고 필요한 곳에 useMemo()를 추가하세요.)

이 마지막 단계는 특히 중간에 있는 컴포넌트의 경우 번거롭습니다. 이상적으로는 컴파일러가 이를 대신 처리해주면 좋겠지만, 미래에는 가능할 수도 있습니다.

이 글에서는 두 가지 다른 기술을 공유하고자 합니다. 이 기술들은 놀랍도록 기본적이어서 사람들이 렌더링 성능을 개선한다는 사실을 잘 깨닫지 못합니다.

이 기술들은 이미 알고 있는 것에 보완적입니다! memo나 useMemo를 대체하지 않지만, 먼저 시도해볼 가치가 있습니다.

다음은 심각한 렌더링 성능 문제를 가진 컴포넌트입니다:

```jsx
import { useState } from 'react';

export default function App() {
  let [color, setColor] = useState('red');
  return (
    <div>
      <input value={color} onChange={(e) => setColor(e.target.value)} />
      <p style={{ color }}>Hello, world!</p>
      <ExpensiveTree />
    </div>
  );
}

function ExpensiveTree() {
  let now = performance.now();
  while (performance.now() - now < 100) {
    // 인위적인 지연 -- 100ms 동안 아무것도 하지 않음
  }
  return <p>I am a very slow component tree.</p>;
}
```

(여기서 시도해보세요)

문제는 App 내부의 color가 변경될 때마다 인위적으로 매우 느리게 만든 <ExpensiveTree />가 다시 렌더링된다는 것입니다.

memo()를 사용하여 해결할 수 있지만, 이에 관한 많은 기존 글들이 있으므로 시간을 할애하지 않겠습니다. 대신 두 가지 다른 해결책을 보여드리겠습니다.

렌더링 코드를 자세히 보면, 반환된 트리의 일부만 현재 color에 관심이 있다는 것을 알 수 있습니다:

```jsx
export default function App() {
  let [color, setColor] = useState('red');
  return (
    <div>
      <input value={color} onChange={(e) => setColor(e.target.value)} />
      <p style={{ color }}>Hello, world!</p>
      <ExpensiveTree />
    </div>
  );
}
```

따라서 해당 부분을 Form 컴포넌트로 추출하고 상태를 아래로 이동시켜 봅시다:

```jsx
export default function App() {
  return (
    <>
      <Form />
      <ExpensiveTree />
    </>
  );
}

function Form() {
  let [color, setColor] = useState('red');
  return (
    <>
      <input value={color} onChange={(e) => setColor(e.target.value)} />
      <p style={{ color }}>Hello, world!</p>
    </>
  );
}
```

(여기서 시도해보세요)

이제 color가 변경되면 Form만 다시 렌더링됩니다. 문제 해결.

위의 해결책은 상태가 비용이 많이 드는 트리 위에 사용되는 경우에는 작동하지 않습니다. 예를 들어, color를 부모 <div>에 두는 경우를 생각해봅시다:

```jsx
export default function App() {
  let [color, setColor] = useState('red');
  return (
    <div style={{ color }}>
      <input value={color} onChange={(e) => setColor(e.target.value)} />
      <p>Hello, world!</p>
      <ExpensiveTree />
    </div>
  );
}
```

(여기서 시도해보세요)

이제 color를 사용하지 않는 부분을 다른 컴포넌트로 