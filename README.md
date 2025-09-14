# NetworkPropagation

RWR(Random Walk with Restart) 기반 **Network Propagation**을 수행해 DEG 시드를 PPI 네트워크 위로 확산시키고, 유전자별 **NP 점수**를 계산합니다. 이후 NP 점수 상위 Top N 유전자와, 그 집합에서 **DEG를 제외한** 유전자 집합 각각에 대해 **Reactome pathway enrichment**를 실행합니다.

## 폴더 구조

```
NetworkPropagation/
├─ network/              # PPI 네트워크(edge list)
├─ DEGs/                 # DEG 목록
├─ results/              # 실행 결과
│  └─ reactome/          # Reactome 분석 결과
└─ source/               # 소스 코드
   ├─ NP.py              # 제공된 Network Propagation 구현
   ├─ utils.py           # 입출력/편의 함수
   ├─ run_pipeline.py    # NP 점수 계산 파이프라인
   └─ enrich_reactome.py # Reactome pathway enrichment
```

## 요구 사항

- Python ≥ 3.9
- OS 제약 없음(Windows/Mac/Linux)
- 인터넷 연결(Reactome 분석 시 `gseapy`의 Enrichr 사용)

설치:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 입력 데이터 형식

### 1) `network/ppi.tsv`
- 탭 구분 edge list
- 포맷: `source<TAB>target<TAB>weight?`
- `weight`는 선택이며 없으면 1로 처리됩니다.
- 예시:
  ```
  TP53	MDM2	1.0
  EGFR	GRB2	0.7
  BRCA1	BRCA2	1.0
  ```

### 2) `DEGs/deg.txt`
- 한 줄에 하나의 유전자 심볼
- 2열에 가중치(선택) 가능. 없으면 1.0으로 처리됩니다.
- 첫 줄에 헤더가 있어도 무시됩니다.
- 예시:
  ```
  GENE	WEIGHT
  TP53	2.4
  EGFR	1.2
  BRCA1
  ```

## 빠른 시작

1) NP 점수 계산

```bash
python source/run_pipeline.py   --ppi network/ppi.tsv   --deg DEGs/deg.txt   --out results/np_scores.tsv   --restart 0.1
```

생성물: `results/np_scores.tsv` (컬럼: `Gene`, `NP_Score`)

2) Reactome pathway enrichment

```bash
python source/enrich_reactome.py   --np_scores results/np_scores.tsv   --deg DEGs/deg.txt   --out results/reactome   --topn 100   --organism Human
```

생성물:
- `results/reactome/reactome_top100.tsv`
- `results/reactome/reactome_top100_noDEG.tsv`

> `gseapy`는 Enrichr의 **Reactome_2016** 라이브러리를 사용합니다. 방화벽/프록시 환경에서는 인터넷 연결이 필요합니다.

## CLI 옵션

### `source/run_pipeline.py`

| 옵션 | 기본값 | 설명 |
|---|---:|---|
| `--ppi` | `network/ppi.tsv` | PPI edge list 입력 경로 |
| `--deg` | `DEGs/deg.txt` | DEG 목록 입력 경로 |
| `--out` | `results/np_scores.tsv` | 유전자별 NP 점수 저장 경로 |
| `--restart` | `0.1` | RWR 재시작 확률 |
| `--normalize` | `false` | 반복 시 확률 벡터 정규화 |
| `--constant_weight` | `false` | 모든 간선 가중치를 동일하게 처리 |
| `--absolute_weight` | `false` | 간선 가중치의 절대값 사용 |
| `--add_bidir` | `false` | 간선을 양방향으로 추가하여 무방향처럼 사용 |

### `source/enrich_reactome.py`

| 옵션 | 기본값 | 설명 |
|---|---:|---|
| `--np_scores` | (필수) | `results/np_scores.tsv` 경로 |
| `--deg` | (필수) | `DEGs/deg.txt` 경로 |
| `--out` | `results/reactome` | 결과 저장 디렉토리 |
| `--topn` | `100` | NP 점수 상위 N 유전자 사용 |
| `--organism` | `Human` | 종 지정(Enrichr 기준, 예: Human/Mouse/Rat) |

## 결과 파일 설명

- `results/np_scores.tsv`  
  유전자별 Network Propagation 점수.
- `results/reactome/reactome_top{N}.tsv`  
  NP 상위 N 유전자로 Reactome pathway enrichment 결과.
- `results/reactome/reactome_top{N}_noDEG.tsv`  
  NP 상위 N에서 DEG를 제외한 집합으로 Reactome 결과.

`gseapy`는 실행 디렉토리에 보조 리포트 파일을 추가로 생성할 수 있습니다.

## 사용 팁

- DEG가 네트워크에 거의 매핑되지 않으면 점수가 전반적으로 희석될 수 있습니다. 유전자 심볼을 최신 표준(HGNC)으로 정리하는 것을 권장합니다.
- 무방향 네트워크처럼 쓰고 싶다면 `--add_bidir` 옵션을 켜세요.
- 간선 가중치의 부호가 섞여 있다면 `--absolute_weight`로 절대값을 사용할 수 있습니다.
- 실행시간은 네트워크 크기, DEG 수, `--restart` 값에 따라 달라집니다.

## 재현성

RWR 과정은 입력이 동일하면 결정적입니다. 동일한 입력 파일과 동일한 옵션으로 실행하면 같은 결과가 나옵니다.

## 문제 해결

- `ModuleNotFoundError: gseapy` → `pip install gseapy`로 설치하세요.
- Reactome 결과가 비어 있음 → 상위 N 유전자에 유효한 심볼이 적거나, Enrichr 연결 문제일 수 있습니다. `--topn`을 늘리거나 네트워크/DEG 매핑을 확인하세요.
- NP 점수가 전부 0에 가깝다 → 네트워크 연결성이 낮거나 DEG가 고립된 경우일 수 있습니다. PPI 품질을 확인하세요.
