---
title: "[논문리뷰] DIFFUSION TRANSFORMERS WITH REPRESENTATION AUTOENCODERS"
date: 2025-10-23 00:00:00 +0900
categories: ["Paper Review", "Image Generation"]
tags: [diffusion-models, dit, rae]
math: true
mermaid: true
---

> [“DIFFUSION TRANSFORMERS WITH REPRESENTATION AUTOENCODERS”](https://arxiv.org/abs/2510.11690) 논문 리뷰입니다.
<details>
<summary>참고 자료</summary>
- 블로그나
- 코드

</details>


---


### Summary

- Diffusion Transformers (DiT)에서 사용되는 VAE Encoder는 과도한 압축으로 인한 정보 부족, outdated backbone, 입력의 의미적인 표현력이 부족하다 등의 단점이 있음.
- 일반적인 통념과 달리, 풍부한 의미적 표현을 사전학습한 representation encoder (e.g., DINO, SigLIP, MAE)에 단순한 transformer decoder를 달아서 학습해도 reconstruction이 가능하다는 것을 보였으며 이를 Representation Autoencoders (RAEs) 라고 명명함.
- 적절히 architecture를 수정하고 학습 방식을 변경하게 되면 RAE를 활용한 DiT 모델이 기존 VAE 기반의 생성 모델들보다 우수한 성능을 보일 수 있을 뿐만 아니라 획기적으로 빠른 수렴 속도를 달성할 수 있음.

### Introduction


Latent diffusion model이나 Diffusion transformer와 같이 최근의 이미지 생성의 표준이 된 모델들은 지난 몇 년간 많은 변화와 발전이 있었지만 어째서인지 latent 공간을 만들어주는 autoencoder 부분은 거의 변화가 없었습니다. 


이 논문에서는 더 풍부한 표현 능력이 있는 representation encoder와 Decoder의 조합으로 autoencoder를 만들고, 이를 통해 DiT의 VAE를 대체해서 생성 품질을 크게 개선하고 수렴 속도도 빨라졌다고 합니다. 저도 VAE가 만들어내는 latent space가 이미지의 semantic을 충분히 반영하지 못하고 있지 않을까 (channel dimension이 고작 4라니..) 어렴풋이 의문을 가졌던 부분이라 흥미롭게 읽었습니다.


### VAE → RAE


Diffusion model들에서 널리 사용되어온 VAE는 몇 가지 문제점이 있는데요,

- latent space를 너무 과도하게 압축하기 때문에 표현력이 부족할 우려가 있습니다. 예를 들면, Stable Diffusion 등에서 사용된 VAE의 경우, 256x256 이미지를 32x32x4 의 latent로 압축하게 됩니다. 과하게 압축을 하다보니 이미지의 의미적인 특성이 잘 반영되지 못해서 representation의 품질이 제한될 수 있는 것이죠.
- 이처럼 capacity가 낮은 latent는 global한 의미적 정보를 담기 어려우며, 이는 곧 생성 모델의 성능 저하로 이어진다는 연구도 있습니다.
- 게다가 연산 측면에서도 비효율적인 문제도 있습니다.

![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-1.png){: width="700" .shadow }


따라서 저자들은 Diffusion model의 VAE를 의미적으로 풍부한 정보를 담을 수 있는 autoencoder로 바꾸는 것을 목표로 합니다. Reconstruction으로만 학습되는 VAE 대신, 풍부한 표현을 사전학습한 DINO, SigLIP과 같은 encoder를 가져다 쓰고 여기에 Decoder를 붙여서 autoencoder로 만드는 것이죠. 


한편, 지난 연구들에 따르면 representation encoder는 high-level semantic에 집중해서 학습되기 때문에 low-level detail은 잘 담지 못하며 따라서 reconstruction task에 부적합하다는 것이 일반적으로 알려져 있는 통념이었습니다. 저자들은 이러한 통념을 반박하며 frozen representation encoder와 단순한 transformer decoder를 가지고도 VAE보다 더 우수하게 reconstruction 할 수 있음을 보였습니다.


Representation Autoencoders (RAE) 는 먼저 frozen representation encoder(e.g., DINO)를 통해 `패치 개수 x hidden dimension` 크기의 latent를 뽑아줍니다. VAE와 차별적인 부분은 hidden dimension이 매우 고차원(768) 이라는 점이죠. 이후 ViT decoder가 이 latent를 받아서 pixel space로 매핑하게 됩니다. 학습 방법도 일반적으로 VAE를 학습할 때 사용되는 training recipe를 그대로 적용했습니다. 아래와 같이 LPIPS loss, L1 loss와 adversarial loss로 구성되어 있습니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-2.png){: width="700" .shadow }


이렇게 학습된 RAE는 VAE보다 우수한 reconstruction 성능을 보일 뿐더러, 연산 효율성도 더 좋습니다. 게다가 VAE와 달리 encoder에서 만들어주는 representation이 의미적인 정보를 충분히 담고있기도 합니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-3.png){: width="700" .shadow }


### RAE로 DiT를 학습시키기


앞서서 RAE가 VAE보다 더 좋을 수 있고 학습 가능하다는 것도 보였지만, DiT와 호환되어서 학습하는 것은 또 다른 문제입니다. 저자들은 먼저 표준적인 학습 방법을 따라서 flow matching objective로 DiT(구체적으로는 LightningDiT를 사용했다고 합니다)를 RAE와 함께 학습해보았습니다. 이 때, **DiT가 처리하는 토큰의 수는 기존의 VAE기반 DiT와 동일하게 설정하였기 때문에 computational overhead는 없다**고 강조합니다. 그런데 학습해본 결과 RAE와 함께 학습된 DiT의 생성 성능은 VAE와 함께 학습된 모델보다 크게 떨어졌습니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-4.png){: width="700" .shadow }


이에 저자들은 이 현상에 대한 몇 가지 가설을 세우고, 각각에 대해 검증하고 검증하는 방식으로 **RAE로 DiT를 잘 학습시키기 위한 방법을 찾아냅니다..!**

1. **DiT 모델 구조가 바뀌어야 한다.**

원래의 DiT는 low dimension을 가지는 VAE의 latent space 위에서 설계된 모델 구조이기 때문에 high dimension의 latent space에 적합하지 않을 수 있습니다. 이에 대한 실험을 하기 위해 저자들은 단 하나의 이미지로 RAE+DiT를 학습시켜보고 reconstruction을 해낼 수 있는지를 통해 본인들의 가설을 검증합니다.


실험해본 결과, RAE에서 뱉어주는 token dimension $n$보다 DiT width(DiT내부에서 사용하는 channel dimension) $d$이 작을 때 학습에 실패하고 큰 성능 저하가 발생합니다. 저자들은 이론적인 근거와 함께 DiT의 width가 커져야 한다는 점을 보이고 향후 실험에서는 **RAE의 token dimension보다 크거나 같은 DiT width를 설정하는 방식으로 DiT 디자인을 변경했습니다.**


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-5.png){: width="700" .shadow }

1. **Noise scheduling이 바뀌어야 한다.**

이전 연구에 따르면 입력의 resolution이 커지게 되면 같은 수준의 noise를 적용했을 때 정보가 손실되는 정도가 줄어들어서 diffusion 학습을 저해한다고 이야기합니다. 동일한 강도의 noise를 가한다고 했을 때, 입력의 크기가 엄청 커진다면 크기가 작을 때보다 이 이미지가 무슨 이미지인지 알아보기 쉬울 것이라 생각한다면 어느정도 이해가 되는 것 같습니다.


한편 diffusion 과정에서 가해지는 Gaussian noise는 channel dimension에도 적용이 되는데, RAE를 사용해서 channel dimension이 매우 커졌다면 비슷한 논리로 noise의 강도가 그에 맞춰서 강해져야하는 것이 아니냐는 주장을 하게 됩니다. **즉, noise의 강도(noise schedule)가 resolution에 의존적이게 설계되는 것이 아니라 token 수와 token의 dimension의 곱으로 정의되는 effective data dimension에 의존적으로 설계되어야 한다고 주장합니다.** 이러한 방식으로 noise schedule을 변경한 결과, 아래와 같이 매우 큰 성능의 향상을 관측할 수 있었습니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-6.png){: width="700" .shadow }

1. **Noise-Augmented Decoding**

VAE는 latent를 continuous한 가우시안 분포로 인코딩하고 이를 디코딩하도록 학습하게 되는 반면, RAE는 discrete한 latent 분포로부터 디코딩하도록 학습됩니다. 한편, Diffusion model은 inference time에 약간의 noisy한 latent를 생성하게 되는데 RAE의 decoder는 discrete한 latent 분포로부터 학습되었기 때문에 이러한 noise가 존재하는 상황에서 잘 복원하기 어려울 수 있을 것입니다.


따라서 저자들은 RAE decoder를 학습할 때 의도적으로 latent에 noise를 랜덤하게 가해서 약간의 noisy한 latent를 받아도 잘 복원하도록 합니다. 실험 결과, noise가 없는 clean한 latent 분포로부터 학습된 경우에 비해 reconstruction 성능은 다소 떨어지더라도 생성품질은 더 향상되는 것을 확인했습니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-7.png){: width="700" .shadow }


이와 같은 실험들을 통해 DiT를 학습하는 테크닉을 전부 적용한 결과 이전 모델들보다 우수한 성능 뿐만 아니라 더 빠른 수렴 속도도 달성할 수 있었습니다.


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-8.png){: width="700" .shadow }


### Model Scalability 개선


앞선 실험들에 의하면 high dimension의 RAE와 호환되게 학습되기 위해서는 DiT의 width가 그에 맞게 커져야 하지만 이는 모델 scale이 커지면 커질수록 연산량이 너무 많아져서 한계가 있습니다. 저자들은 이런 한계를 극복하기 위해 효율적으로 DiT의 width를 키울 수 있는 방법을 고안합니다.


DiT의 원래 width를 유지하되, 마지막에 2-layer의 2048 dimension으로 구성된 transformer module의 DDT head를 부착함으로써 효율적으로 model width를 키울 수 있게 됩니다. 이러한 테크닉까지 종합적으로 적용해서 저자들은 Diffusion Transformer에서의 SOTA를 달성했습니다. 


![image.png](/assets/img/posts/2025/2025-10-23-논문리뷰-diffusion-transformers-with-representation-au-9.png){: width="700" .shadow }


### Conclusion


학계에서 일반적으로 알려져있던 통념을 정면으로 반박한 점이 매우 인상깊은 논문이었습니다. 또한, DiT 학습이 잘 안되는 점에 대해서 여러 가설을 세우고 이를 하나씩 검증해나가면서 개선하는 점이 참 배울 점이 많다고 느껴집니다. Diffusion model의 새로운 표준을 제시한 것 같아서 얼마나 큰 임팩트가 있을지 기대가 됩니다.

