---
title: "[논문리뷰] Denoising Diffusion Probabilistic Models (DDPM)"
date: 2025-11-06 00:00:00 +0900
categories: ["Paper Review", "Image Generation"]
tags: [diffusion-models, ddpm, generative-models]
math: true
---

> ["Denoising Diffusion Probabilistic Models"](https://arxiv.org/abs/2006.11239) (Ho et al., NeurIPS 2020) 논문 리뷰입니다.

<details markdown="1">
<summary>참고 자료</summary>

- [DDPM Paper](https://arxiv.org/abs/2006.11239)
- [Official Code](https://github.com/hojonathanho/diffusion)
- [Understanding Diffusion Models: A Unified Perspective](https://arxiv.org/pdf/2208.11970)
- [DSBA 연구실 Paper review 영상](https://www.youtube.com/watch?v=_JQSMhqXw-4&t=1951s)

</details>

---

## Summary

- Diffusion model의 기초가 되는 연구로, 데이터에 점진적으로 노이즈를 추가하는 forward process와 이를 역으로 제거하는 reverse process를 학습
- ELBO 기반의 목적식을 단순화하여 노이즈를 예측하는 문제로 변환
- 어려운 denoising task에 집중할 수 있도록 weighting 계수를 제거하여 생성 품질을 크게 향상
- 이후 수많은 diffusion 기반 생성 모델 연구의 토대가 된 핵심 논문

<br>

## Introduction

최근 몇 년간 "diffusion"이라는 키워드가 AI 연구 분야 전반에 셀 수 없을만큼 등장하고 있습니다. 본 포스팅에서는 수많은 diffusion-based generative model 관련 연구에 큰 영향을 미쳤던 연구이자, diffusion model의 기본이 되는 "Denoising Diffusion Probabilistic Models" 논문을 자세히 살펴보고자 합니다.

깨끗한 물이 담긴 컵에 빨간색 색소를 몇 방울 떨어뜨리면 색소가 점차 확산되어 전체적으로 붉은 색을 띄는 액체가 되듯이, 실제 관측되는 이미지 데이터에 아주 작은 노이즈를 계속해서 더한다면 점점 형태를 알아보기 어렵다가 결국 이미지와 동일한 크기의 노이즈가 될 것입니다. 이러한 확산 현상(diffusion)의 개념을 활용한 generative model이 바로 diffusion model입니다.

<br>

## What is Diffusion Model?

먼저, diffusion model이라는 것에 대해 직관적으로 이해해 보겠습니다. 우리가 생성 모델을 통해 알고 싶은 것은 실제 데이터의 분포 $x \sim p(x)$ 입니다. 하지만 $p(x)$ 는 매우 고차원이고 복잡하기 때문에 쉽게 알 수 없습니다. Diffusion model도 하나의 생성 모델이며, 복잡한 $p(x)$ 를 모델링하기 위해 사용되는 직관은 꽤나 단순합니다.

$x_0$ 를 실제 이미지 데이터라고 해봅시다. 이 이미지에 아주 작은 노이즈를 추가하는 작업을 수천번 진행하면 어떻게 될까요? 아래의 그림처럼 한 남성의 사진인 $x_0$ 으로부터 충분히 큰 $T$ 번만큼 아주 작은 노이즈를 추가하면 같은 크기의 무작위 노이즈 이미지 $x_T$ 가 될 것입니다.

그런데 만약 우리가 "아주 작은 노이즈를 추가하는 작업"을 반대로 할 수 있으면(즉, 노이즈를 걷어내는 작업) 임의의 노이즈로부터 그럴듯한 이미지를 생성하는 것도 가능하지 않을까요? Diffusion model에서는 작은 노이즈를 여러번 추가하는 작업을 반대로 하는 방법을 찾는 모델이라고 볼 수 있습니다.

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-1.png){: width="700" .shadow }

<br>

## Formal Definition of Diffusion Model

Diffusion model은 우리가 정확하게 알지 못하는 잠재 변수를 도입하는 latent variable model 중의 하나라고 볼 수 있습니다. 이미지 데이터를 $x_0 \sim q(x_0)$ 라고 할 때 diffusion model은 $x_1, x_2, ..., x_T$ 를 $x_0$ 와 동일한 차원을 가지는 latent variable로 도입합니다.

$$
p_\theta (x_0) := \int p_\theta (x_{0:T}) dx_{1:T}
$$

일반적인 latent variable model (e.g., VAE)에서 잠재 변수 $z$ 를 도입하듯이, 이 경우에 $x_1, x_2, ..., x_T$ 를 도입했다고 이해하면 되겠습니다.

<br>

### Forward (Diffusion) Process

Forward process는 작은 노이즈를 데이터에 추가하는 과정을 의미합니다. Diffusion model에서는 원본 이미지 $x_0$ 으로부터 $x_1, x_2, ..., x_T$ 에 이르는 forward process를 Markov chain으로 정의합니다. Markov chain은 특정 시점의 상태가 오로지 직전 상태에만 의존한다는 특징이 있습니다.

Forward process에서는 variance schedule $\beta_1, ..., \beta_T$ 에 따라 Gaussian 노이즈를 점차 증가시키는 것으로 transition을 정의합니다. 즉, forward process를 의미하는 posterior $q(x_{1:T} \mid x_0)$ 는 다음과 같습니다.

$$
\begin{aligned}
q(x_{1:T} \mid x_0) &:= \prod_{t=1}^T q(x_t \mid x_{t-1}), \\
q(x_t \mid x_{t-1}) &:= \mathcal{N}(x_t ; \sqrt{1-\beta_t}x_{t-1},\beta_t \mathbf{I})
\end{aligned}
$$

$\beta_t$ 가 1에 가까울수록 노이즈가 커서 standard Gaussian 분포에 비슷해지고 0에 가까울수록 노이즈가 작아서 이전 상태인 $x_{t-1}$ 에 가까워지게 됩니다.

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-2.png){: width="800" .shadow }

<br>

### Reverse Process

우리가 diffusion model에서 알고 싶은 것은 노이즈를 추가하는 forward process를 이용해서 노이즈를 걷어내는 과정, 즉 reverse process입니다. 노이즈를 추가하는 과정은 $q(x_t \mid x_{t-1})$ 으로 정의하였으므로, 반대로 노이즈를 걷어내는 과정은 $q(x_{t-1} \mid x_t)$ 가 될 것입니다.

하지만 $q(x_{t-1} \mid x_t)$ 을 알아내는 것은 매우 어렵기 때문에, diffusion model에서는 $\theta$ 라는 파라미터를 갖는 모델 $p_\theta$ 를 이용해서 이 조건부 확률 분포를 근사하고자 합니다.

다행히도, forward process가 충분히 작은 노이즈를 가질 때($\beta_t$ 가 작을 때) reverse process도 Gaussian 분포를 따른다는 것이 알려져 있습니다. 따라서 $p_\theta(x_{t-1} \mid x_t)$ 를 Gaussian 분포의 형태로 정의하고 그 Gaussian 분포가 어떤 평균과 분산을 갖는 분포인지 잘 찾아주면 될 것입니다.

따라서, reverse process $p_\theta(x_{0:T})$ 는 forward process와 유사하게 Gaussian transition을 가지는 Markov chain으로 정의합니다.

$$
\begin{aligned}
p_\theta(x_{0:T}) &:= p(x_T)\prod_{t=1}^T p_\theta(x_{t-1} \mid x_t), \\
p_\theta(x_{t-1} \mid x_t) &:= \mathcal{N}(x_t ; \mu_\theta(x_t,t),\Sigma_\theta(x_t,t))
\end{aligned}
$$

$\mu_\theta(x_t,t), \Sigma_\theta(x_t,t)$ 는 학습을 통해 얻어야 하는 대상으로, 각각 $x_t$ 와 $t$ 를 인자로 받는 function으로 이해하면 되겠습니다.

<br>

### Training Objective (ELBO)

Diffusion model에서는 다른 generative model(e.g., VAE)과 유사하게 log-likelihood를 최대화하도록 $p_\theta$ 를 학습합니다. 목적식을 유도하는 과정은 VAE에서 ELBO를 유도하는 과정과 대체로 유사합니다.

<br>

#### ELBO (Evidence Lower Bound) 유도

Variational lower bound라고도 알려져 있는 ELBO는 Variational Bayesian method에서 사용되는 개념으로, VAE에서도 등장합니다.

주어진 관측값 $x$ 를 활용해서 이것의 분포 $p(x)$ 를 알고 싶은 경우가 많은데, $p(x)$ 는 일반적으로 매우 복잡하기 때문에 쉽게 알기 어렵습니다. 따라서 우리가 무엇인지 잘 알지는 못하지만, 비교적 단순한 분포를 따르는 변수를 도입하곤 합니다. 이 때의 변수를 잠재 변수(latent variable)라고 하며, $z$ 로 표현하겠습니다.

잠재 변수를 도입해서 복잡한 $p(x)$ 를 비교적 단순한 분포인 $p(z)$ 를 적절히 조합해서 표현해낼 수 있다면 결과적으로 $p(x)$ 를 알 수 있을 것입니다.

$$
p(x) = \int p(x,z) dz = \int p(x \mid z)p(z) dz
$$

$\theta$ 를 파라미터로 갖는 모델 $p_\theta(x \mid z)$ 를 도입해서 $p(x \mid z)$ 를 근사하고, 관측값 $x$ 의 정보를 활용해서 $z$ 를 추론하는 $q_\phi(z \mid x)$ 를 도입합니다.

이를 활용해서 $p_\theta$ 의 log-likelihood를 유도하면:

$$
\begin{aligned}
\log p_\theta(x) &= \log \int_z p_\theta(x,z) ~dz \\
&= \log \int_z p_\theta(x \mid z)p(z) ~dz \\
&= \log \int_z p_\theta(x \mid z)p(z) \frac{q_\phi(z \mid x)}{q_\phi(z \mid x)}  ~dz \\
&= \log \mathbb{E}_{z \sim q_\phi(z \mid x)} \left[\frac{p_\theta(x \mid z)p(z)}{q_\phi(z \mid x)}\right] \\
&\geq \mathbb{E}_{z \sim q_\phi(z \mid x)} \left[\log \frac{p_\theta(x \mid z)p(z)}{q_\phi(z \mid x)}\right] \quad (\text{Jensen's inequality})
\end{aligned}
$$

마지막에 구해지는 lower bound를 Evidence Lower Bound (ELBO)라고 부릅니다. 이를 더 전개하면:

$$
\log p_\theta(x) \geq \mathbb{E}_{z \sim q_\phi(z \mid x)} [ \log p_\theta(x \mid z) ] - D_{KL}(q_\phi (z \mid x) \| p(z))
$$

최종적으로 두 가지 term으로 정리됩니다. 첫 번째 항은 reconstruction term에 해당하고, 두 번째 항은 posterior $q_\phi(z \mid x)$ 가 prior $p(z)$ 와 유사하도록 하는 regularization term에 해당합니다.

<br>

#### Diffusion Model의 ELBO

Diffusion model도 하나의 latent variable model입니다. 위 예시에서는 $z$ 라는 하나의 잠재 변수를 도입했던 것과는 달리, diffusion model에서는 $x_0$ 와 동일한 dimensionality를 갖는 $T$ 개의 잠재 변수 $x_1, x_2, ..., x_T$ 를 도입한 것입니다.

$p_\theta$ 의 실제 데이터 $x_0$ 에 대한 log-likelihood로부터 ELBO를 유도하면 다음과 같습니다:

$$
\begin{aligned}
\log p_\theta(x_0) &= \log \int p_\theta(x_{0:T})~ dx_{1:T} \\
&= \log \int p_\theta(x_{0:T}) \frac{q(x_{1:T} \mid x_0)}{q(x_{1:T} \mid x_0)} ~ dx_{1:T} \\
&= \log \mathbb{E}_{q(x_{1:T} \mid x_0)} \left[ \frac{p_\theta(x_{0:T})}{q(x_{1:T} \mid x_0)} \right] \\
&\geq \mathbb{E}_{q(x_{1:T} \mid x_0)} \left[ \log \frac{p_\theta(x_{0:T})}{q(x_{1:T} \mid x_0)} \right]
\end{aligned}
$$

여기서 forward process와 reverse process의 정의를 활용해서 위의 ELBO 식을 다시 써보면:

$$
\begin{aligned}
L &= \mathbb{E}_{q(x_{1:T} \mid x_0)} \left[ \log \frac{p_\theta(x_{0:T})}{q(x_{1:T} \mid x_0)} \right] \\
&= \mathbb{E}_{q(x_{1:T} \mid x_0)} \left[ \log \frac{p(x_T)\prod_{t=1}^{T}{p_\theta (x_{t-1} \mid x_t)}}{\prod_{t=1}^{T}{q(x_t \mid x_{t-1})}} \right]
\end{aligned}
$$

오른쪽 항을 보면 $p_\theta(x_{t-1} \mid x_t)$ 와 $q(x_t \mid x_{t-1})$ 이 target으로 하는 variable이 서로 다릅니다. 앞에서 우리는 $q$ 를 Markov chain으로 정의했었는데, Markov property를 활용해서 $q(x_t \mid x_{t-1})$ 을 변형할 수 있습니다:

$$
\begin{aligned}
q(x_t \mid x_{t-1}) &= q(x_t \mid x_{t-1},x_0) \quad (\text{Markov property}) \\
&= \frac{q(x_t,x_{t-1},x_0)}{q(x_{t-1},x_0)} \\
&= \frac{q(x_t,x_{t-1},x_0)}{q(x_{t-1},x_0)} \cdot \frac{q(x_t,x_0)}{q(x_t,x_0)} \\
&= q(x_{t-1} \mid x_t,x_0)\cdot \frac{q(x_t \mid x_0)}{q(x_{t-1} \mid x_0)}
\end{aligned}
$$

이 결과를 ELBO 식에 대입하고 전개하면 (telescoping 과정을 거쳐):

$$
\begin{aligned}
L &= -D_{KL}( q(x_T \mid x_0) \| p(x_T) ) \\
&\quad - \sum_{t=2}^{T} \mathbb{E}_{q(x_t \mid x_0)} \left[ D_{KL}(q(x_{t-1} \mid x_t,x_0) \| p_\theta(x_{t-1} \mid x_t)) \right] \\
&\quad + \mathbb{E}_{q(x_1 \mid x_0)} [ \log p_\theta (x_0 \mid x_1) ]
\end{aligned}
$$

최종적으로 목적식이 3개의 항으로 구성됩니다:

**1) $L_T$ 항**

$$
L_T = D_{KL}( q(x_T \mid x_0) \| p(x_T) )
$$

최종적으로 노이즈가 추가된 입력이 standard Gaussian prior와 얼마나 유사한지를 나타냅니다.

**2) $L_{t-1}$ 항**

$$
L_{t-1} = \mathbb{E}_{q(x_t \mid x_0)} \left[ D_{KL}(q(x_{t-1} \mid x_t,x_0) \| p_\theta(x_{t-1} \mid x_t)) \right]
$$

$t$ 시점의 reverse step이 ground truth reverse step과 얼마나 유사한지를 나타냅니다. 원본 데이터인 $x_0$ 가 조건으로 주어진 상황에서는 tractable하게 계산 가능합니다.

**3) $L_0$ 항**

$$
L_0 = -\mathbb{E}_{q(x_1 \mid x_0)} \left[ \log p_\theta (x_0 \mid x_1) \right]
$$

가장 마지막 reconstruction을 의미합니다 (VAE의 reconstruction loss와 유사).

<br>

#### 계산을 위한 두 가지 핵심 분포

위 Loss를 계산하기 위해 두 가지 term을 구해야 합니다: (1) $q(x_t \mid x_0)$ 와 (2) $q(x_{t-1} \mid x_t,x_0)$

**Forward result at step $t$: $q(x_t \mid x_0)$**

$$
q(x_t \mid x_0) = \mathcal{N}\left(x_t;\sqrt{\bar{\alpha_t}}x_0,(1-\bar{\alpha_t})\mathbf{I} \right)
$$

여기서 $\alpha_t=1-\beta_t$, $\bar{\alpha_t}=\prod_{i=1}^{t}{\alpha_i}$ 입니다.

<details markdown="1">
<summary>유도 과정 보기</summary>

$t$ 시점의 샘플 $x_t$ 를 reparameterization trick을 이용하면 다음과 같이 쓸 수 있습니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-5.png){: width="600" .shadow }

한편, $\epsilon_t$ 와 $\epsilon_{t-1}$ 은 모두 standard Gaussian으로부터 샘플링 되는 확률 변수이기 때문에 두 확률 변수의 합을 새로운 확률 변수로 표현할 수 있습니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-6.png){: width="700" .shadow }

이를 이용해서 다시 $x_t$ 를 좀 더 간단히 쓸 수 있습니다. 이러한 과정을 $x_0$ 까지 반복하면 $x_t$ 를 $x_0$ 를 이용해서 쓸 수 있습니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-7.png){: width="700" .shadow }

즉, $q(x_t \mid x_0)$ 는 $\mathcal{N}(x_t;\sqrt{\bar{\alpha_t}}x_0,(1-\bar{\alpha_t})\mathbf{I})$ 의 reparameterization form으로 표현됩니다.

</details>

<br>

**Reverse Posterior: $q(x_{t-1} \mid x_t,x_0)$**

$$
q(x_{t-1} \mid x_t,x_0)=\mathcal{N}\left( x_{t-1}; \frac{\sqrt{\alpha_t}(1-\bar{\alpha}_{t-1})x_t + \sqrt{\bar{\alpha}_{t-1}}(1-\alpha_t)x_0}{1-\bar{\alpha_t}} , \frac{(1-\alpha_t)(1-\bar{\alpha}_{t-1})}{1-\bar{\alpha}_t}\mathbf{I} \right)
$$

<details markdown="1">
<summary>유도 과정 보기</summary>

위에서 $q(x_t \mid x_0)$ 와 $q(x_{t-1} \mid x_0)$ 을 구한 것과 Bayes rule을 활용해서 유도할 수 있습니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-8.png){: width="800" .shadow }

</details>

<br>

## DDPM의 핵심 개선사항

DDPM 논문에서는 diffusion model의 목적식을 획기적으로 간소화하고, 그 결과로 높은 품질의 이미지를 생성하는 성능을 달성하였습니다.

<br>

### 1. $L_T$ 를 상수로 취급

DDPM에서는 forward process에서 노이즈의 정도를 나타내는 variance $\beta_t$ 를 learnable하게 두지 않고 상수로 취급하였습니다. 따라서 $L_T$ 항은 학습 대상에서 제외됩니다.

<br>

### 2. 노이즈 예측 방식으로 재정의

앞서 $p_\theta (x_{t-1} \mid x_t) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t),\Sigma_\theta(x_t,t))$ 로 정의했기 때문에 $x_t$ 와 $t$ 를 인자로 받는 두 함수 $\mu_\theta(x_t, t), \Sigma_\theta(x_t,t)$ 를 어떤 형태로 정의할지 결정해주어야 합니다.

먼저, DDPM에서는 variance term을 $t$ 에만 의존하는 상수로 정의합니다 (i.e., $\Sigma_\theta(x_t,t) = \sigma_t^2 \mathbf{I}$). 논문에서는 $\sigma_t^2 = \beta_t$ 로 하거나 $\sigma_t^2 = \frac{(1-\alpha_t)(1-\bar{\alpha}_{t-1})}{1-\bar{\alpha}_t}$ 로 설정하는 두 경우가 결과에 큰 차이를 주지 않는다고 설명합니다.

다음으로 $\mu_\theta(x_t,t)$ 를 결정해주어야 하는데, $L_{t-1}$ 항을 아래와 같이 전개했을 때 얻어지는 형태로부터 착안합니다. $q$ 와 $p_\theta$ 모두 Gaussian임을 이용하면 KL divergence term은 아래와 같이 표현됩니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-9.png){: width="700" .shadow }

위 수식에서 가장 straightforward하게 $\mu_\theta$ 를 정의하자면 posterior의 평균인 $\tilde{\mu}_t$ 를 예측하도록 하는 함수가 될 것입니다. 한편, 앞에서 $q(x_t \mid x_0)$ 를 구할 때 사용했던 reparameterization trick을 동일하게 사용하면 $\tilde{\mu}_t (x_t,x_0)$ 를 다시 쓸 수 있습니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-10.png){: width="700" .shadow }

가까워지도록 만들고자 하는 대상인 posterior의 평균이 위와 같은 형식이고, 우리가 정의하려는 함수는 $x_t,t$ 를 인자로 받는 함수입니다. 따라서 마지막 줄에 있는 것처럼 $\epsilon$ 을 예측하는 역할을 하는 $\epsilon_\theta$ 를 도입해서 $\mu_\theta$ 를 정의한 것입니다. 이를 정리하면 최종적으로 아래와 같은 수식으로 정리됩니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-3.png){: width="700" .shadow }

즉, 우리가 $L_t$ 를 minimize한다는 것은 결국 우리의 모델이 $t$ 시점의 noisified sample을 만들기 위해 샘플링된 Gaussian noise $\epsilon$ 을 잘 예측하도록 만든다는 것과 같다는 것을 알 수 있습니다.

<br>

### 3. 최종 목적식 $L_{simple}$

저자들은 한 단계 더 나아가서, 계수에 해당하는 term을 삭제합니다. 따라서 최종 목적식은:

$$
L_{simple} = \mathbb{E}\left[|| \epsilon - \epsilon_\theta(x_t,t)||^2_2 \right]
$$

논문에 따르면, 계수를 삭제함으로써 작은 $t$ 에 대해 loss가 상대적으로 적게 반영되는 효과를 얻을 수 있습니다. $t$ 가 작은 값을 가지는 시점은 원본으로부터 노이즈가 별로 추가되지 않은 시점이기 때문에 denoising task 자체가 쉬운 상황으로 생각할 수 있습니다.

따라서 저자들은 $t$ 가 큰 시점에서 어려운 denoising task에 더 잘 집중할 수 있도록 하기 위해 계수를 제거했으며, 실험적으로도 더 나은 결과를 얻었다고 이야기합니다.

<br>

## Algorithm

최종적으로 학습과 샘플링 과정은 아래와 같이 진행됩니다:

![image](/assets/img/posts/2025/2025-11-06-논문리뷰-denoising-diffusion-probabilistic-models-4.png){: width="700" .shadow }

**Training Algorithm**:
- 모든 $t$ 에 대해 단계적으로 노이즈를 가하는 것이 아니라, 임의의 $t$ 를 샘플링한 후 해당 $t$ 에 대한 목적식의 gradient를 바로 구하는 것으로 진행됩니다
- 각 iteration에서 데이터 $x_0$ 를 샘플링하고, 시점 $t$ 를 랜덤하게 선택
- $q(x_t \mid x_0)$ 를 이용해 노이즈를 추가하고, 모델이 추가된 노이즈 $\epsilon$ 을 예측하도록 학습

**Sampling Algorithm**:
- Initial noise $x_T \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ 로부터 시작
- 이미 학습된 모델을 통해 단계적으로 denoising을 진행하는 방식으로 이미지를 생성
- $t = T$ 부터 $t = 1$ 까지 역순으로 진행하며, 각 단계에서 $p_\theta(x_{t-1} \mid x_t)$ 로부터 샘플링

<br>

## 마치며

여기까지 DDPM 논문에서 제안한 방법을 최대한 자세하게 알아보았습니다. 기존에 있던 diffusion model을 수학적으로 개량하는 것을 통해 다른 generative model과 버금가는 생성 결과를 얻어낸 것이 주요 contribution이라고 생각됩니다.

특히 DDPM의 핵심적인 기여는 다음과 같습니다:

- **목적식의 단순화**: 복잡한 ELBO를 노이즈 예측 문제로 변환

$$
\|\epsilon - \epsilon_\theta(x_t,t)\|^2
$$

- **효율적인 학습**: Weighting 계수를 제거하여 어려운 denoising task에 집중
- **이론과 실제의 균형**: 수학적으로 엄밀하면서도 구현이 간단한 알고리즘 제시

이후 Stable Diffusion, DALL-E, Imagen 등 수많은 diffusion 기반 생성 모델들의 토대가 된 매우 중요한 논문이며, 앞으로 diffusion model을 공부하실 때 이 내용이 도움이 되었으면 좋겠습니다.
