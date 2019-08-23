# tkch_batch_fbx_export

Bleder で FBX export する際の定形操作を自動化するアドオン

## Description

VRChat用のアバターモデルをBlenderで改変し、Unityに持っていくためにFBXエクスポートしますが、  
FBXエクスポートのたびに

1. 次の改変で使うため別名で保存
1. ミラーモディファイアの適用
1. メッシュオブジェクトの結合
1. シェイプキーの順序変更

というお決まりの操作をします。  
面倒くさい上によく間違えるので、バッチ処理するアドオンを作成しました。

設定をPythonのコードで定義する必要がありますが、  
結合パターンを段階ごとに複数設定できます。  
Mikoko、Nekoma向けの設定をサンプルとして定義してあります。

動作確認環境
- Bleder 2.80
- Blender 2.79  [2.79用ブランチ](https://github.com/eijis-pan/tkch_batch_fbx_export/blob/Blender2.79/tkch_batch_fbx_export.py)

## Install

1ファイルで構成されたアドオンです。
`編集`→`プリファレンス`→`アドオン`→`インストール...` で tkch_batch_fbx_export.py を指定してください。

## Usage

3Dビューポートのサイドバーに「結合済みFBX出力」パネルが追加されます。  
実行したバッチ処理名（モデル定義名）のボタンを押すとファイルを保存するウィンドウ（ファイル・ブラウザ）が表示されます。  
`バッチ処理で使用する新規の作業ファイル` ボタンを押すとBlenderファイルが別名で保存されバッチ処理後にFBXファイルがエクスポートされます。  
処理後は別名のファイルが変更された状態で開いています。不要であれば後で手動で削除してください。  

結合パターンを編集する場合は tkch_batch_fbx_export.py ファイルの24行目から154行目にかけて  
'モデル情報定義' があるのでそこに追加もしくは変更してください。  
Blender起動中にaddonディレクトリ内のファイルを直接変更した場合はアドオンを再有効化してください。  
別の場所にあるファイルを修正した場合はアドオンを削除して再インストールしてください。

## 既知の不具合

[wiki / 開発メモ](https://github.com/eijis-pan/tkch_batch_fbx_export/wiki/%E9%96%8B%E7%99%BA%E3%83%A1%E3%83%A2)を見てね。

## Author

github:[eijis](https://github.com/eijis-pan)  または twitter: @ eijis_pan

## Licence

[MIT Licence](https://github.com/eijis-pan/tkch_batch_fbx_export/LICENCE) 

## Disclaimer

利用は自己責任でお願いします。  
本プログラムは、なんの欠陥もないという無制限の保証を行うものではありません。  
本プログラムに関する不具合修正や質問についてのお問い合わせもお受けできない場合があります。  
本プログラムの利用によって生じたあらゆる損害に対して、一切の責任を負いません。  
本プログラムの利用によって生じるいかなる問題についても、その責を負いません。
