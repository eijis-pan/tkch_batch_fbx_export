# ------------------------------------------------------------------------------------------------------------ #
#
# アドオン情報
#


bl_info = {
    "name": "結合済みFBX出力",
    "author": "eijis-pan",
    "version": (0, 4),
    "blender": (2, 79, 0),
    # "blender": (2, 80, 0),
    "location": "View3D > Sidebar",
    "description": "Mikoko、Nekoma向けFBX出力の事前処理自動化アドオン: \
ミラーモディファイア適用、オブジェクト結合、シェイプキー順序変更を段階ごとに行いFBX出力する",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "https://github.com/eijis-pan/tkch_batch_fbx_export/tree/Blender2.79",
    "tracker_url": "",
    "category": "Import-Export"
}


# ------------------------------------------------------------------------------------------------------------ #
#
# モデル情報定義
#


# 定数の様な使い方をするので大文字にする


class MODEL_INFO:
    # 扱うモデルの種類。ボタンの表示や、定義のキーとして使う
    MODEL_NAMES = (
        'Mikoko',
        'Nekoma',
    )

    # オブジェクト結合のルールで残り全てを表す定数
    ALL_OBJ_KEY = "\tALL\t"  # [tab]ALL[tab] で残り全てを表す

    #
    # オブジェクト結合のルール
    #

    # モデル名をキーにした連想配列（値は段階別の結合ルール定義）
    OBJ_JOIN_GROUPS = {
        #
        # オブジェクト結合ルール（段階別として複数定義できる）
        #   要素は連想配列
        #     連想配列のキー：グループ名（fbx出力のファイル名）
        #     連想配列の値：オブジェクト結合ルールの連想配列
        #
        MODEL_NAMES[0]: {  # Mikoko
            #
            # オブジェクト結合ルールの連想配列
            #     連想配列のキー：結合先のオブジェクト名（オブジェクトが見つからない場合は処理せず続行）
            #     連想配列の値：結合するオブジェクト名の配列（タプル）
            #                 オブジェクト名として [tab]ALL[tab] を指定すると残り全てを表す
            #                 オブジェクトが見つからない場合は処理せず続行
            #
            # 先頭から順に処理されるので、細かいものほど前に定義する必要がある（一度結合したものは分割されない）
            # 全く違うパターンで結合したい場合は、別モデルとして定義を作成し、別のボタンにする必要がある Mikoko2 とか
            #
            'face_skin_clothes': {  # 顔と体と服を分ける設定
                #
                # ALL_OBJ_KEY を持つものを最後にする処理を入れています。
                # （必ずしも ALL_OBJ_KEY を使う必要はありません。）
                #
                'Clothes_Outerwear': (
                    'Clothes_Outerwear',  # 結合先と同じものはあってもなくても良い
                    'Clothes_BellFront', 'Clothes_Sleeve', 'Clothes_Skirt',
                    'Clothes_RibbonBack', 'Clothes_RibbonFront', 'Clothes_Ribbon_Neck',
                    'Shoes_Geta',
                ),
                'Face': (
                    'Face',  # 結合先と同じものはあってもなくても良い
                    'Face_Manpu_Tears', 'Face_Mouth', 'Mimi', 'Mimi_Ke',
                    'Hair_Back', 'Hair_Bell', 'Hair_Clip', 'Hair_Front', 'Hair_Option', 'Hair_Side',
                    'Eye_Circle', 'Eye_kira', 'Eye_Line', 'Eye_main', 'Eye_X',
                ),
                'Skin': (ALL_OBJ_KEY,),
            },
            'face_and_other': {  # 顔とそれ以外を分ける設定
                'Face': ('Face',),
                'Skin': (ALL_OBJ_KEY,),
            },
            'all_in_one': {  # 全てを１つに結合する設定（アバターランクをExcellentにするため）
                'Skin': (ALL_OBJ_KEY,),
            },
        },
        MODEL_NAMES[1]: {  # Nekoma
            'fix_from_master': {  # NekomaMaster_1.01.fbx から NekomaFix_1.01.fbx 相当へ結合する設定
                'Clothes_Batwing': ('Clothes_Batwing',),
                'Clothes_Robe': ('Clothes_Button', 'Clothes_Mimi', 'Clothes_Robe_Frill', 'Clothes_Shoes',),
                'Eye_Main': ('Eye_Main',),
                'Eye_X': ('Eye_Circle', 'Eye_Hart', 'Eye_Kira', 'Eye_Line', 'Eye_Tears',),  # NekomaFix_1.01.fbx では Eye_SpecialEff に相当
                'Face': ('Face',),
                'Face_Mouth': ('Face_Tongue', ),
                'Ghost': ('Ghost',),
                'Hair_Front': ('Hair_Front',),
                'Tail': ('Tail_Button',),
                'Body': (ALL_OBJ_KEY,),  # 残り全て
            },
            'face_and_other': {  # 顔とそれ以外で分ける設定
                'Face': (
                    'Face_Mouth', 'Hair_Front', 'Eye_X',
                    'Eye_SpecialEff',  # NekomaFix_1.01.fbx の場合は Eye_* がまとめられている
                    # ↓ 前段の fix_from_master で結合され、消えていたとしても無視して続行される
                    'Face_Tongue', 'Eye_Circle', 'Eye_Hart', 'Eye_Kira', 'Eye_Line', 'Eye_Main', 'Eye_Tears',
                ),
                'Body': (ALL_OBJ_KEY,),  # 残り全て
            },
            'all_in_one': {  # 全てを１つに結合する設定（アバターランクをExcellentにするため）
                'Body': (ALL_OBJ_KEY,),  # 全て
            },
        },
    }

    #
    # アイトラッキング用にシェイプキーの順番を入れ替える情報
    #   オブジェクト名に関わらず順番を入れ替えが行われる
    #   （Unityに持って行ってからオブジェクト名を変更する運用も考えられるため）
    #
    # アイトラッキングが有効になる条件を満たさない場合、順番が変わっても影響なし
    #   条件の例：RootのBone名称が「Armature」である
    #           シェイプキーのオブジェクト名が「Body」である
    #           他にBoneの構成にも条件があるが、このアドオンではシェイプキーの順番しか扱わない
    #
    EYE_T_KEYS = {
        # モデル名をキーにした連想配列
        # 全く使わない場合は連想配列を定義しない、もしくは空を定義しておく
        MODEL_NAMES[0]: {  # Mikoko
            #
            # シェイプキーの順番入れ替えルールの連想配列
            #     連想配列のキー：シェイプキー名（シェイプキーが見つからない場合は処理せず続行）
            #     連想配列の値：最終的に配置したいインデックス（0はBasisを指すので1〜4）
            #
            # 順位を上にあげる処理しか入れていないので、値は昇順で定義すること
            # （値が4でも最初から3の位置にあった場合、3のままで4に下げる処理はされない。この場合1〜3を処理することで4になる）
            #
            'EyeClose_L': 1,
            'EyeClose_R': 2,
            'Eyebrows_Infront_L': 3,  # 目下部のすぼまり（左）に該当するシェイプキーを充てるべきだが、変化がほとんどないものを充てておく
            'Eyebrows_Infront_R': 4,  # 目下部のすぼまり（右）に該当するシェイプキーを充てるべきだが、変化がほとんどないものを充てておく
        },
        MODEL_NAMES[1]: {  # Nekoma
            'Close_Eye_L': 1,
            'Close_Eye_R': 2,
            'Down_Eyebrows_L': 3,  # 目下部のすぼまり（左）に該当するシェイプキーを充てるべきだが、変化がほとんどないものを充てておく
            'Down_Eyebrows_R': 4,  # 目下部のすぼまり（右）に該当するシェイプキーを充てるべきだが、変化がほとんどないものを充てておく
        },
    }


# ------------------------------------------------------------------------------------------------------------ #
#
# Python モジュールの import
#


import os
import datetime

# ------------------------------------------------------------------------------------------------------------ #
#
# Blender 関連モジュールの import
#

# Blender の Pythonコンソールを参考に
#
# Builtin Modules:     bpy, bpy.data, bpy.ops, bpy.props, bpy.types, bpy.context, bpy.utils, bgl, blf, mathutils
# Convenience Imports: from mathutils import *; from math import *
# Convenience Variables: C = bpy.context, D = bpy.data


import bpy
from bpy import data
from bpy import ops
from bpy import props
from bpy import types
from bpy import context
from bpy import utils
import bgl
import blf
import mathutils

from mathutils import *
from math import *

# C = bpy.context
# D = bpy.data

from bpy.props import StringProperty


# ------------------------------------------------------------------------------------------------------------ #
#
# アドオン用クラスとアドオン定型処理
#


# モデル選択パネル
class TKCH_PT_MainEntryPanel(bpy.types.Panel):
    bl_label = bl_info['name']
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = bl_info['name']
    # bl_context = "objectmode"  # オブジェクトモードに限定する場合に指定する

    def draw_header(self, context_):
        layout = self.layout
        layout.label(text="", icon='PLUGIN')

    def draw(self, context_):
        layout = self.layout

        # すでに処理済みの場合、警告メッセージを表示する
        if IntegratedExporter.is_working_file_opened(context_):
            layout.label(text="FBX出力に使用した作業ファイルが開かれています。", icon='ERROR')
        else:
            if not context_.blend_data.is_dirty:
                layout.label(text="データ保存済み", icon='PACKAGE')
            else:
                # 保存されていない場合、警告メッセージを表示する
                layout.label(text="現在編集中のデータは保存されていません。", icon='ERROR')

        # モデル定義ごとにボタンを表示する
        for model_name in MODEL_INFO.MODEL_NAMES:
            ot = layout.operator(TKCH_OT_PreProcessAndFBXExport.bl_idname, text=model_name)
            ot.model_name = model_name


# モデル別実行ボタンの処理
class TKCH_OT_PreProcessAndFBXExport(bpy.types.Operator):
    bl_idname = "tkch.preprocess_fbxexport"
    bl_label = "バッチ処理で使用する新規の作業ファイル"  # "バッチ処理で使用する新規の作業ファイル名を入力して保存してください。"
    bl_description = bl_info['description']
    bl_options = {'REGISTER', 'UNDO'}

    ''' 
    # 2.79 用
    filepath = StringProperty(subtype="FILE_PATH")
    filename = StringProperty(subtype="FILE_NAME")
    directory = StringProperty(subtype="FILE_PATH")
    model_name = StringProperty(default=MODEL_INFO.MODEL_NAMES[0], options={"HIDDEN"})
    '''

    # 2.80 用
    filepath: StringProperty(subtype="FILE_PATH")
    filename: StringProperty(subtype="FILE_NAME")
    directory: StringProperty(subtype="FILE_PATH")
    model_name: StringProperty(default=MODEL_INFO.MODEL_NAMES[0], options={"HIDDEN"})

    def invoke(self, context_, event):

        # 現在のファイル名にタイムスタンプを付加して新規ファイル名のデフォルトとする
        dt_now = datetime.datetime.now()
        current_filepath = context_.blend_data.filepath
        path_split_list = os.path.split(current_filepath)
        file_name = path_split_list[-1]
        ext_split_list = os.path.splitext(file_name)
        ext = ext_split_list[-1] if 1 < len(ext_split_list) else ''
        temp_file_name = ext_split_list[0] + '_' + dt_now.strftime('%Y%m%d_%H%M%S') + ext
        self.filename = temp_file_name

        # ファイルブラウザ表示
        wm = context_.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context_):

        # 作業ファイルが新規であることを確認
        if os.path.exists(os.path.join(self.directory, self.filename)):
            self.report({'WARNING'}, '指定された作業ファイル名は既に存在しています。処理を中止しました。')
            return {'CANCELLED'}

        # バッチ処理呼び出し
        if not IntegratedExporter.preprocess_and_export(
                context_=context_,
                operator=self,
                model_name=self.model_name,
                working_file=self.filename,
                directory=self.directory,
                # debug=True,  # 開発用 ログ出力の設定
        ):
            self.report({'WARNING'}, 'FBX出力はエラーで中断しました。')
            return {'CANCELLED'}

        self.report({'INFO'}, 'FBX出力は正常に終了しました。')
        return {'FINISHED'}


classes = [
    TKCH_PT_MainEntryPanel,
    TKCH_OT_PreProcessAndFBXExport,
]


# アドオン有効化時の処理
def register():
    for c in classes:
        bpy.utils.register_class(c)


# アドオン無効化時の処理
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


# メイン処理（開発用に直接実行する場合のエントリポイント、Add-on状態では実行されない）
if __name__ == "__main__":
    register()


# ------------------------------------------------------------------------------------------------------------ #
#
# バッチ処理
#

# アドオンのインストールが楽になるので、ソースを1ファイルに記述
# 関数をまとめる目的でクラスのスタティックメソッドとして定義する

import logging
import logging.config


class IntegratedExporter:
    # クラス変数
    _opened_working_file = None

    # 既に処理済みかどうかを、ファイルパスを比較して判定するメソッド
    @staticmethod
    def is_working_file_opened(context_):
        return IntegratedExporter._opened_working_file == context_.blend_data.filepath

    #
    # バッチ処理のエントリポイント
    #
    @staticmethod
    def preprocess_and_export(context_, operator, model_name, working_file, directory, debug=False):

        if debug:
            # 開発用 ログ出力の設定
            dt_now = datetime.datetime.now()
            logging.basicConfig(
                filename=bpy.path.abspath('//') + __name__ + dt_now.strftime('_%Y%m%d') + '.log',
                level=logging.DEBUG,
            )

        logging.debug("==== " + model_name + " ====")
        result = False
        try:
            # 別名でコピーして作業する
            working_file_path = os.path.join(directory, working_file)
            ops.wm.save_as_mainfile(filepath=working_file_path)
            IntegratedExporter._opened_working_file = working_file_path

            ext_split_list = os.path.splitext(working_file)
            filename_prefix = ext_split_list[0]

            # レイヤーを全て表示する
            if hasattr(context_, 'view_layer'):
                logging.debug('___ data.collections ___')
                for (k, v) in bpy.data.collections.items():
                    v.hide_viewport = False
                logging.debug('=== layer_collection ===')
                for (k, v) in context_.window.view_layer.layer_collection.children.items():
                    logging.debug('view_layer: ' + v.name)
                    v.exclude = False
                    v.hide_viewport = False
            else:
                for i in range(len(context_.scene.layers)):
                    context_.scene.layers[i] = True

            # ミラーモディファイアを適用する（ミラーモディファイアが設定されているオブジェクトすべて）
            IntegratedExporter._all_mirror_modifier_apply(context_=context_)

            # 段階ごとにオブジェクトを結合する
            group_list = MODEL_INFO.OBJ_JOIN_GROUPS[model_name] if model_name in MODEL_INFO.OBJ_JOIN_GROUPS else None
            if group_list:

                # アイトラッキング用シェイプキー入れ替え情報
                eye_t_keys = MODEL_INFO.EYE_T_KEYS[model_name] if model_name in MODEL_INFO.EYE_T_KEYS else None

                '''
                # 2.79 Python 3.7 未満 から連想配列の順番が保証されないのでキーで昇順ソートする
                group_list_keys = sorted(group_list.keys())
                for group_name in group_list_keys:
                    obj_join_groups = group_list[group_name]
                '''
                # 2.80 Python 3.7 から連想配列の順番が保証される
                for group_name, obj_join_groups in group_list.items():

                    logging.debug('グループ名： ' + group_name)
                    # オブジェクトを結合する
                    IntegratedExporter._mesh_combine_by_group(context_=context_, groups=obj_join_groups)
                    # アイトラッキング用にシェイプキーの順番を入れ替える
                    IntegratedExporter._shapekey_sort_for_eyetracking(context_=context_, eye_t_keys=eye_t_keys)
                    # fbx 出力
                    filename = filename_prefix + '_' + group_name + '.fbx'
                    ops.export_scene.fbx(filepath=os.path.join(directory, filename))
                    operator.report({'INFO'}, 'FBXファイルを出力しました。[ ' + filename + ' ]')

        except Exception as ex:

            operator.report({'WARNING'}, '例外発生')
            operator.report({'DEBUG'}, str(ex))
            logging.debug('例外発生')
            logging.debug(ex)

        else:

            logging.debug('正常終了')
            result = True

        return result

    #
    # ミラーモディファイアを適用する（ミラーモディファイアが設定されているオブジェクトすべて）
    #
    @staticmethod
    def _all_mirror_modifier_apply(context_):
        logging.debug('ミラーモディファイアを適用する（ミラーモディファイアが設定されているメッシュオブジェクトすべて）')
        count = 0
        for obj in bpy.data.objects:
            if not isinstance(obj.data, types.Mesh):
                continue

            for mod in obj.modifiers:
                if not isinstance(mod, types.MirrorModifier):
                    continue

                logging.debug('--- ' + obj.name + ' ---')
                logging.debug('    ' + mod.name)

                if hasattr(context_, 'view_layer'):
                    context_.view_layer.objects.active = obj
                else:
                    context_.scene.objects.active = obj

                if hasattr(obj, 'select_set'):
                    obj.select_set(True)
                else:
                    obj.select = True

                try:
                    ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                except Exception as ex:
                    logging.debug('modifier_apply error!')
                    logging.debug(ex)
                else:
                    count += 1
                    logging.debug('modifier_apply success')

        logging.debug('modifier_apply success count ' + str(count))
        return

    #
    # オブジェクトを結合する
    #
    @staticmethod
    def _mesh_combine_by_group(context_, groups):
        logging.debug('オブジェクトを結合する')

        # 全てが対象に指定されているものは後回しにする
        group_keys = []
        for head, members in groups.items():
            if MODEL_INFO.ALL_OBJ_KEY in members:
                group_keys.append(head)
            else:
                group_keys.insert(0, head)

        joined_names = []
        for head in group_keys:
            members = groups[head]

            logging.debug('--- ' + head + ' ---')

            # 全てが対象に指定されているか
            all_flg = MODEL_INFO.ALL_OBJ_KEY in members
            logging.debug('  all_flg: ' + str(all_flg))

            # if len(members) <= 1 and not all_flg:
            #    logging.debug('group skip (single member)')
            #    continue

            head_found = False
            found_member_count = 0
            for obj in bpy.data.objects:
                if not isinstance(obj.data, types.Mesh):
                    if hasattr(obj, 'select_set'):
                        obj.select_set(False)
                    else:
                        obj.select = False
                    continue

                if obj.name not in members and head != obj.name and not all_flg:
                    if hasattr(obj, 'select_set'):
                        obj.select_set(False)
                    else:
                        obj.select = False
                    continue

                if all_flg and obj.name in joined_names:
                    if hasattr(obj, 'select_set'):
                        obj.select_set(False)
                    else:
                        obj.select = False
                    continue

                logging.debug('    ' + obj.name)

                if hasattr(obj, 'select_set'):
                    obj.hide_set(False)
                    obj.select_set(True)
                else:
                    obj.hide = False
                    obj.select = True
                found_member_count += 1
                joined_names.append(obj.name)

                if head == obj.name:

                    if hasattr(context_, 'view_layer'):
                        context_.view_layer.objects.active = obj
                    else:
                        context_.scene.objects.active = obj

                    logging.debug('active ' + obj.name)
                    head_found = True

            if not head_found or (found_member_count <= 0):
                logging.debug('group skip (aleady joined)')
                continue

            try:
                ops.object.join()
            except Exception as ex:
                logging.debug('object join error!')
                logging.debug(ex)
            else:
                logging.debug('object join success')

        logging.debug('success mesh_combine_by_group')
        return

    #
    # アイトラッキング用にシェイプキーの順番を入れ替える
    #
    @staticmethod
    def _shapekey_sort_for_eyetracking(context_, eye_t_keys):

        if not eye_t_keys:
            return

        logging.debug('アイトラッキング用にシェイプキーの順番を入れ替える')

        for obj in bpy.data.objects:
            if not isinstance(obj.data, types.Mesh):
                continue

            # if 'Body' != obj.name:
            #    logging.debug(obj.name + ' skip (not Body)')
            #    continue

            logging.debug('--- ' + obj.name + ' ---')

            if hasattr(context_, 'view_layer'):
                context_.view_layer.objects.active = obj
            else:
                context_.scene.objects.active = obj

            if hasattr(obj, 'select_set'):
                obj.select_set(True)
            else:
                obj.select = True

            i = 0
            while True:
                context_.object.active_shape_key_index = i
                if context_.object.active_shape_key is None:
                    break

                shape_key_name = context_.object.active_shape_key.name
                logging.debug('    ' + str(i) + ':' + shape_key_name)
                if shape_key_name not in eye_t_keys:
                    i += 1
                    continue

                goal_index = eye_t_keys[shape_key_name]
                logging.debug('   >' + str(goal_index))
                if i <= goal_index:
                    logging.debug('   - noop')
                    i += 1
                    continue
                for j in range(i - goal_index):
                    logging.debug('   + up')
                    ops.object.shape_key_move(type='UP')

                i += 1

        return
