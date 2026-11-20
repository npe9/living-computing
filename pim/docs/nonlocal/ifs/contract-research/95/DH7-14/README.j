MGTP利用のための各種ユーティリティ
====================================================
1996年5月10日
九州大学		長谷川 隆三

[1] MGTPとは

MGTP(Model Generation Theorem Prover)はモデル生成法に基づく一階述語論
理の定理証明システムです．含意形式(MG節と呼ぶ)で与えられた問題をモデル
生成法によって解きます．

MGTPは, MG節集合をKL1節集合に変換し，これとKL1で書かれたMGTP推論エンジ
ンをKLICシステムでコンパイル・リンクすることにより，証明を行う方式をとっ
ています．

これまでは，MG節をKL1節に変換する「MGTPトランスレータ」は，SICStus
Prolog上で動作しましたが，今回はKLIC上で動作するものを配布します．
今回配布するソフトウェアは，これを含めて全てKLIC上で動作します．

(1) MGTPトランスレータ：MG節をKL1節に変換

(2) インタプリタ版MGTP：MG節を直接入力し証明を行うMGTP推論エンジン

(3) 各種開発支援ツール

(4) 探索空間剪定のための前処理システム(FD変換器とNHM変換器)

(5) MGTPトレーサ：MGTP証明の過程のトレース

(6) KLICの対話的実行環境

[2] 利用想定者：IFS(90) MGTP/G(KLIC版)の利用者

[2] 実行環境

KLIC 2.002 以上が動作する環境であれば動作するはずです．

現版は以下の UNIX システムでは動作を確認しています.

Sun SparcStation 10 running SunOS 5.3 (Solaris 2.3)
                with gcc-2.6.3
Sun SparcStation 10 running SunOS 5.4 (Solaris 2.4)
                with gcc-2.6.3
Gateway P5-120 and some other PC/AT compatibles
                running Linux 1.3.9 (Slackware 2.3.0)
                with gcc-2.6.3

[3] ドキュメント

ps形式のマニュアルがディレクトリ "documents" の下にあります．

[4] ファイル

ファイルについては MANIFEST と御覧下さい.

[5] インストール

マニュアルを御覧下さい．

[7] バグについて

バグ報告やコメントは下記のアドレスにお送り下さい.

        koshi@ar.is.kyushu-u.ac.jp

見つけたバグや不具合は是非お知らせ下さい.  すべてのユーザのための次版
以降の改良のためにたいへん大事な情報です.

