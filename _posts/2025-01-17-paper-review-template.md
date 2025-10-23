---
title: "[논문리뷰] ResNet: Deep Residual Learning for Image Recognition"
date: 2025-01-17 00:00:00 +0900
categories: [Paper Review, Computer Vision]
tags: [resnet, cnn, deep-learning, image-classification]
math: true
mermaid: true
# image:
#   path: /assets/img/papers/resnet-architecture.png
#   alt: ResNet Architecture
---

## 논문 정보
- **제목**: Deep Residual Learning for Image Recognition
- **저자**: Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
- **발표**: CVPR 2016
- **논문 링크**: [arXiv:1512.03385](https://arxiv.org/abs/1512.03385)

## TL;DR
- 매우 깊은 네트워크 학습을 위한 Residual Learning 프레임워크 제안
- Skip connection을 통해 gradient vanishing 문제 해결
- ImageNet에서 152층 네트워크로 SOTA 달성

## 1. Introduction

### 문제 정의
딥러닝에서 네트워크가 깊어질수록 성능이 좋아질 것으로 예상되지만, 실제로는:
- Gradient vanishing/exploding 문제
- Degradation problem: 깊은 네트워크가 얕은 네트워크보다 오히려 성능이 떨어짐

### 핵심 아이디어
Residual Learning: $H(x) = F(x) + x$
- $H(x)$를 직접 학습하는 대신 $F(x) = H(x) - x$를 학습
- Identity mapping을 통한 skip connection

## 2. Method

### Residual Block

![Residual Block Structure](/assets/img/posts/2025/residual-block.png){: width="500" }
_그림 1: ResNet의 기본 Residual Block 구조_

```python
def residual_block(x, filters):
    # F(x) 부분
    identity = x

    x = conv2d(x, filters, 3)
    x = batch_norm(x)
    x = relu(x)

    x = conv2d(x, filters, 3)
    x = batch_norm(x)

    # H(x) = F(x) + x
    x = x + identity
    x = relu(x)

    return x
```

### 수식 설명

Residual block의 forward pass:
$$y = F(x, \{W_i\}) + x$$

여기서:
- $x$: 입력
- $y$: 출력
- $F(x, \{W_i\})$: 학습해야 할 residual mapping
- $W_i$: 각 층의 가중치

Backpropagation에서의 gradient:
$$\frac{\partial \mathcal{L}}{\partial x} = \frac{\partial \mathcal{L}}{\partial y} \cdot \frac{\partial y}{\partial x} = \frac{\partial \mathcal{L}}{\partial y} \cdot (1 + \frac{\partial F}{\partial x})$$

## 3. Architecture

![ResNet Architecture Comparison](/assets/img/posts/2025/resnet-architectures.png){: width="800" .shadow }
_그림 2: ResNet-34와 VGG-19, Plain-34 네트워크 구조 비교_

### ResNet 구조 비교

| Model | Layers | Parameters | Top-1 Error |
|-------|--------|------------|-------------|
| ResNet-18 | 18 | 11.7M | 30.43% |
| ResNet-34 | 34 | 21.8M | 26.73% |
| ResNet-50 | 50 | 25.6M | 24.01% |
| ResNet-101 | 101 | 44.5M | 22.44% |
| ResNet-152 | 152 | 60.2M | 21.69% |

## 4. Experiments

### ImageNet 결과
- ILSVRC 2015 classification 1위
- 3.57% top-5 error rate
- 이전 SOTA 대비 상대적 성능 향상 28%

### Ablation Study
1. **Plain Network vs ResNet**
   - 34층에서 ResNet이 Plain network보다 낮은 error
   - 152층 ResNet이 34층 Plain network보다 좋은 성능

2. **Projection Shortcuts**
   - Identity shortcuts이 projection shortcuts보다 효율적

## 5. 구현 코드

```python
import torch
import torch.nn as nn

class BasicBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride, 1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out
```

## 6. Discussion

### 장점
- 매우 깊은 네트워크 학습 가능
- 구현이 간단하고 직관적
- 다양한 vision task에 적용 가능

### 한계점
- 메모리 사용량이 많음
- Skip connection으로 인한 추가 메모리 필요
- 매우 깊은 네트워크에서는 여전히 학습 어려움 존재

## 7. Conclusion

ResNet은 딥러닝 역사에서 가장 영향력 있는 아키텍처 중 하나입니다. Skip connection이라는 간단한 아이디어로 깊은 네트워크 학습 문제를 해결했고, 이후 DenseNet, ResNeXt, EfficientNet 등 많은 후속 연구의 기반이 되었습니다.

## References
1. He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. CVPR.
2. [Official PyTorch Implementation](https://github.com/pytorch/vision/blob/master/torchvision/models/resnet.py)

---

**Keywords**: #ResNet #DeepLearning #ComputerVision #CNN #ResidualLearning