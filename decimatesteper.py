import bpy
import os
from bpy.props import FloatProperty, IntProperty,StringProperty,EnumProperty

bl_info = {
    "name": "decimate steper",
    "author": "minimal97",
    "version": (0, 7),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > decimate_steper",
    "description": "",
    "category": "Interface",
}


# =======================================================================
#
# プロパティグループの定義
#
class MyAddonProperties(bpy.types.PropertyGroup):
    Decimate_param: FloatProperty(
        name="数値",
        description="浮動小数点数の入力",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    texsize: EnumProperty(
        name="値",
        description="スライダーの値を選択",
        items=[
            ('1', "1", "値を1に設定"),
            ('2', "2", "値を2に設定"),
            ('4', "4", "値を4に設定"),
            ('8', "8", "値を8に設定"),
        ],
        default='4'
    )

    org_obj: StringProperty(
        name="Original Obj",
        description="",
        default="",
    )
    
    copied_obj: StringProperty(
        name="Copied Obj",
        description="",
        default="",
    )

    newTexturename: StringProperty(
        name="新規テクスチャ名",
        description="texture name",
        default="",
    )
    
    Texturesize: StringProperty(
        name="参考サイズ",
        description="参考サイズ",
        default="",
    )


# =======================================================================
# オペレーターの定義
#
class SimpleOperator(bpy.types.Operator):
    bl_idname = "object.simple_operator"
    bl_label = "オブジェクトをコピー"
    
    def execute(self, context):
        # 選択されているオブジェクトを取得
        selected_objects = bpy.context.selected_objects

        # 選択されているオブジェクトの数を確認
        if len(selected_objects) == 1:
            obj = selected_objects[0]
            if obj.type == 'MESH':
                
                bpy.context.view_layer.objects.active = obj
                context.scene.my_tool.org_obj = obj.name
                bpy.ops.object.duplicate()
                context.scene.my_tool.copied_obj = bpy.context.active_object.name
        else:
            self.report({'ERROR'}, 'オブジェクトが選択されていません。')
            
        return {'FINISHED'}


# =======================================================================
#
#
#
def merge_by_distance(distance=0.0002):
    # 選択中のオブジェクトを処理
    obj = bpy.context.active_object
    
    # 編集モードに切り替え
    original_mode = obj.mode
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # 頂点数を取得（処理前）
    bpy.ops.object.mode_set(mode='OBJECT')
    vertices_before = len(obj.data.vertices)
    bpy.ops.object.mode_set(mode='EDIT')
    
    # すべての頂点を選択
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Merge by Distanceを実行
    bpy.ops.mesh.remove_doubles(threshold=distance)
    
    # 頂点数を取得（処理後）
    bpy.ops.object.mode_set(mode='OBJECT')
    vertices_after = len(obj.data.vertices)
    
    # 元のモードに戻す
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=original_mode)
    
    print(f"{vertices_before - vertices_after} 頂点が結合されました (閾値: {distance}m)")


# =======================================================================
#
# オペレーターの定義
#
class MeshMergebyDistance(bpy.types.Operator):
    bl_idname = "object.meshcleanup"
    bl_label = "Merge by Distance 0.0002m"
    
    def execute(self, context):
        if (check_Select_Single() == True):
            merge_by_distance(0.0002)
            self.report({'INFO'},'MeshMergebyDistance')
        else :
            self.report({'ERROR'},'オブジェクトは1つ選択')
            
        return {'FINISHED'}


# =======================================================================
#
# オペレーターの定義
#
def delete_loose_geometry():
    # 選択されたオブジェクト（1つのみ前提）
    obj = bpy.context.active_object
    
    # 現在のモードを保存
    original_mode = obj.mode
    
    # 編集モードに切り替え
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # すべての要素を選択
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Delete Looseを実行（facesも含める）
    bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=True)
    
    # 元のモードに戻す
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=original_mode)
    
    print(f"オブジェクト '{obj.name}' で Delete Loose を実行しました（loose faces含む）")


# =======================================================================
#
# オペレーターの定義
#
class MeshDeleteLoose(bpy.types.Operator):
    bl_idname = "object.deleteloose"
    bl_label = "Delete Loose"
    
    def execute(self, context):
        if (check_Select_Single() == True):
            delete_loose_geometry()
            
        else:
            self.report({'ERROR'},'オブジェクトは1つ選択')
            
        return {'FINISHED'}
    

# =======================================================================
#
#
#
def check_Select_Single():
    # 選択されているオブジェクトを取得
    selected_objects = bpy.context.selected_objects
    # 選択されているオブジェクトの数を確認
    if len(selected_objects) == 1:
        obj = selected_objects[0]
        if obj.type == 'MESH':
            return True
        else:
            return False
    return False


# =======================================================================
#
#
#
def smart_uv_unwrap_selected():
    """
    選択中のオブジェクトに対してSmart UV Unwrapを実行する関数
    """                    
    # 編集モードになっていない場合は、現在のモードを保存して編集モードに切り替える
    original_mode = bpy.context.object.mode
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # すべての面を選択
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Smart UV Projectを実行
    #bpy.ops.uv.smart_project(
        #angle_limit=66.0,  # 角度制限（デフォルト値）
    #    angle_limit = 0.349066,
    #    island_margin=0.001,  # アイランド間のマージン
    #    area_weight=0.0,  # 面積の重み
    #    rotate_method='AXIS_ALIGNED',  # 回転方法をaxis-alignedに設定
    #    correct_aspect=True  # アスペクト比の修正
    #)

    bpy.ops.uv.smart_project(angle_limit=0.349066, margin_method='SCALED', rotate_method='AXIS_ALIGNED', island_margin=0.000, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    
    # 元のモードに戻す
    if original_mode != 'EDIT':
        bpy.ops.object.mode_set(mode=original_mode)
    
    print(f"Smart UV Unwrap applied to: {bpy.context.object.name}")


# =======================================================================
#
#
#
def show_modifier_panel(self):
    # プロパティエディタの位置を特定し、モディファイアに切り替え
    for area in bpy.context.screen.areas:
        if area.type == 'PROPERTIES':
            for space in area.spaces:
                if space.type == 'PROPERTIES':
                    # プロパティスペースをモディファイアに切り替え
                    space.context = 'MODIFIER'
            return True



# =======================================================================
#
# Decimate Panel botton
#
class DecimatePaneOperator(bpy.types.Operator):
    bl_idname = "object.decimatepaneoperator"
    bl_label = "デシメートあてる"

    def execute(self, context):
        # 選択されているオブジェクトを取得
        selected_objects = bpy.context.selected_objects

        # 選択されているオブジェクトの数を確認
        if len(selected_objects) == 1:
            obj = selected_objects[0]
            if obj.type == 'MESH':
                has_decimate = False
                for modifier in obj.modifiers:
                    if modifier.type == 'DECIMATE':
                        has_decimate = True
                        break
                
                if not has_decimate:
                    # デシメートモディファイアを追加
                    decimate_mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
                    # デフォルト設定（比率0.5）
                    decimate_mod.ratio = 0.5
                    self.report({'INFO'}, 'デシメートモディファイアを適用しました。')

                else:
                    self.report({'INFO'}, 'デシメート適用済み。')

                show_modifier_panel(self)
                
            else:
                self.report({'ERROR'}, 'デシメートモディファイアを適用できません。')
        else:
            # 選択されているオブジェクトが1つではない場合
            if len(selected_objects) == 0:
                self.report({'ERROR'}, 'オブジェクトが選択されていません。')
            else:
                self.report({'ERROR'}, 'デシメートモディファイアを適用するには1つだけ選択してください。')
        return {'FINISHED'}


# =======================================================================
#
# Texture Creat Panel botton
#
class GetTextureNameOperator(bpy.types.Operator):
    bl_idname = "object.gettexturenameoperator"
    bl_label = "テクスチャ情報"
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        
        if len(selected_objects) == 1:
            obj = selected_objects[0]
            if obj.type == 'MESH':
                    # マテリアルを持っているか確認
                if obj.material_slots:
                    # 最初のマテリアルスロットからマテリアルを取得
                    material = obj.material_slots[0].material
                    if material:
                        # ノードベースのマテリアルかチェック
                        if material.use_nodes:
                            # テクスチャノードを探す
                            texture_found = False
                            for node in material.node_tree.nodes:
                                # テクスチャノードを特定（主なテクスチャノードタイプ）
                                if node.type == 'TEX_IMAGE' and node.image:
                                    texture_name = node.image.name
                                    last_comma_index = texture_name.rfind('.')
                                    
                                    # コンマが見つかった場合、その前の部分を取得
                                    if last_comma_index != -1:
                                        newtexturename = texture_name[:last_comma_index]
                                    else:
                                        # コンマがない場合は元の名前をそのまま使用
                                        newtexturename = texture_name
                                        
                                    newtexturename = newtexturename + '2'
                                    newtexturename = create_unique_texture_name(newtexturename)
                                    self.report({'INFO'},f"テクスチャ名: {node.image.name}")
                                    self.report({'INFO'},f"テクスチャ名: {newtexturename}")
                                    context.scene.my_tool.newTexturename = newtexturename
                                    
                                    width = node.image.size[0]
                                    height = node.image.size[1]
                                    #size = height + 'x' + width
                                    context.scene.my_tool.Texturesize = str(height) + 'x' + str(width)
                                    
                                    texture_found = True
                                    break
                            
                            if not texture_found:
                                print(f"マテリアル '{material.name}' は画像テクスチャを使用していません。")
                        else:
                            # 従来のテクスチャシステム（古いバージョン用）
                            if hasattr(material, 'texture_slots') and material.texture_slots:
                                for slot in material.texture_slots:
                                    if slot and slot.texture and slot.texture.type == 'IMAGE':
                                        print(f"テクスチャ名: {slot.texture.name}")
                                        if slot.texture.image:
                                            print(f"テクスチャファイルパス: {slot.texture.image.filepath}")
                                        texture_found = True
                                        break
                                
                                if not texture_found:
                                    print(f"マテリアル '{material.name}' は画像テクスチャを使用していません。")
                            else:
                                print(f"マテリアル '{material.name}' はテクスチャを使用していません。")
                    else:
                        print(f"マテリアル")
                
        return {'FINISHED'}


# =======================================================================
#
#
#
def check_existImageName(base_name=""):
    
    # 既存の全画像名をリストアップ
    existing_names = [img.name for img in bpy.data.images]
    
    # 基本名がまだ存在しない場合はそのまま返す
    if base_name in existing_names:
        return True
    else:
        return False


# =======================================================================
#
#
#
def create_unique_texture_name(base_name=""):
    """既存の画像名と重複しない一意の名前を生成する"""
    
    # 既存の全画像名をリストアップ
    existing_names = [img.name for img in bpy.data.images]
    
    # 基本名がまだ存在しない場合はそのまま返す
    if base_name not in existing_names:
        return base_name
    
    # 重複する場合は連番を付ける
    counter = 1
    new_name = f"{base_name}.{counter:03d}"
    
    # 重複しない名前が見つかるまで連番を増やす
    while new_name in existing_names:
        counter += 1
        new_name = f"{base_name}.{counter:03d}"
    
    return new_name


# =======================================================================
#
#
#
def new_material_with_texture(obj, texture_path=None, material_name="New_Material"):
    """
    指定したオブジェクトのマテリアルをすべて削除し、
    新しいマテリアルを作成してテクスチャを適用する関数
    
    Parameters:
    obj (bpy.types.Object): マテリアルをリセットするオブジェクト
    texture_path (str): テクスチャのファイルパス（Noneの場合はテクスチャを適用しない）
    material_name (str): 作成する新しいマテリアルの名前
    
    Returns:
    bpy.types.Material: 作成された新しいマテリアル
    """
    # オブジェクトが有効かチェック
    if not obj or obj.type != 'MESH':
        print(f"エラー: 有効なメッシュオブジェクトではありません ({obj.name if obj else 'None'})")
        return None
    
    # オブジェクトからすべてのマテリアルスロットを削除
    while obj.material_slots:
        bpy.ops.object.material_slot_remove()
    
    # 新しいマテリアルの作成
    new_material = bpy.data.materials.new(name=material_name)
    new_material.use_nodes = True  # ノードを使用する
    
    # オブジェクトにマテリアルを追加
    obj.data.materials.append(new_material)
    
    # テクスチャを適用（パスが指定されている場合）
    if texture_path:
        existing_image = bpy.data.images[texture_path]
        # マテリアルのノードツリーを取得
        nodes = new_material.node_tree.nodes
        links = new_material.node_tree.links
        
        # デフォルトのノードをクリア
        nodes.clear()
        
        # プリンシプルBSDFシェーダーを追加
        principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_node.location = (300, 300)
        
        # マテリアル出力ノードを追加
        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (600, 300)
        
        # テクスチャイメージノードを追加
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.location = (0, 300)
        
        # ノード同士を接続
        # テクスチャのColor出力をプリンシプルBSDFのBase Colorに接続
        links.new(tex_node.outputs["Color"], principled_node.inputs["Base Color"])
        
        # プリンシプルBSDFのBSDFをマテリアル出力のSurfaceに接続
        links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])

        # イメージを読み込む
        try:
            tex_node.image = existing_image
            print(f"テクスチャをロードしました: {texture_path}")
        except Exception as e:
            print(f"テクスチャのロードに失敗しました: {e}")
            return new_material

    print(f"オブジェクト '{obj.name}' に新しいマテリアル '{new_material.name}' を適用しました")
    if texture_path:
        print(f"テクスチャ '{texture_path}' を適用しました")
    
    return new_material


# =======================================================================
#
# 使用例：選択されたすべてのオブジェクトにこの関数を適用
#
def apply_to_selected_objects(texture_path=None, material_name="New_Material"):
    """選択されたすべてのオブジェクトに新しいマテリアルとテクスチャを適用する"""
    selected_objects = bpy.context.selected_objects
    applied_count = 0
    
    for obj in selected_objects:
        if obj.type == 'MESH':
            new_material_with_texture(obj, texture_path, material_name)
            applied_count += 1
    
    print(f"{applied_count}個のオブジェクトにマテリアルを適用しました")

# 実行例
# テクスチャのパスを指定して関数を呼び出す
# apply_to_selected_objects(texture_path="C:/path/to/your/texture.png", material_name="New_Material")

# テクスチャなしで新しいマテリアルのみを適用する例
# apply_to_selected_objects(material_name="Plain_Material")


# =======================================================================
#
# Texture Creat Panel botton
#
class TextureCreateOperator(bpy.types.Operator):
    bl_idname = "object.texturecreatoperator"
    bl_label = "テクスチャ作成"
    
    def execute(self, context):
        
        if check_existImageName(context.scene.my_tool.newTexturename) == True:
            self.report({'ERROR'},"ファイル名が重複")
            
        else:
            new_image = bpy.data.images.new(
                name=context.scene.my_tool.newTexturename,
                width=int(context.scene.my_tool.texsize) * 1024,
                height=int(context.scene.my_tool.texsize) * 1024,
                alpha=False
            )
            self.report({'INFO'},"TextureCreate")
            
        return {'FINISHED'}


# =======================================================================
#
# Texture Creat Panel botton
#
class SmartUVOperator(bpy.types.Operator):
    bl_idname = "object.smartuvoperator"
    bl_label = "SmartUV適応"
    
    def execute(self, context):
        if (check_Select_Single() == True):
            
            selected_objects = bpy.context.selected_objects
            # 選択されているオブジェクトの数を確認
            if len(selected_objects) == 1:
                obj = selected_objects[0]
                if obj.type == 'MESH':
                    has_decimate = False
                    for modifier in obj.modifiers:
                        if modifier.type == 'DECIMATE':
                            has_decimate = True
                            self.report({'ERROR'},"DECIMATE")
                            return {'FINISHED'}

                
            smart_uv_unwrap_selected()
        else:
            self.report({'ERROR'},"SmartUVOperator")
        return {'FINISHED'}

# =======================================================================
# Texture Creat Panel botton
class MaterialOperator(bpy.types.Operator):
    bl_idname = "object.materialoperator"
    bl_label = "新規マテリアル適用"
    
    def execute(self, context):
        if (check_Select_Single() == True):
            apply_to_selected_objects(context.scene.my_tool.newTexturename, "New_Material")
        
        return {'FINISHED'}
    
    
# =======================================================================
def setup_bake_settings():
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True

    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = 0.01

    try:
        # Blender 3.x系
        bpy.context.scene.render.bake.margin_type = 'EXTEND'
    except AttributeError:
        # 古いバージョンのBlenderでは別の属性名かもしれない
        print("注意: margin_typeが見つかりませんでした。Blenderのバージョンを確認してください。")
        # 古いバージョンでは以下を試してみてください
        # bpy.context.scene.render.bake.margin_type = 'CLAMP'

    bpy.context.scene.render.bake.margin = 16  # 任意のマージン値


# =======================================================================
# Texture Creat Panel botton
class TextureBakeOperator(bpy.types.Operator):
    bl_idname = "object.texturebakeoperator"
    bl_label = "テクスチャベイク準備"
    
    def execute(self, context):
        setup_bake_settings()
        return {'FINISHED'}


# =======================================================================
# Texture Creat Panel botton
class TextureBakeStart(bpy.types.Operator):
    bl_idname = "object.texturebakestart"
    bl_label = "テクスチャベイク"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        
        if context.scene.my_tool.copied_obj in bpy.data.objects:
            # オブジェクトを選択してアクティブに設定
            copied_obj = bpy.data.objects[context.scene.my_tool.copied_obj]
            copied_obj.select_set(True)
            bpy.context.view_layer.objects.active = copied_obj
        
        else:
            print("happysocks_outオブジェクトが見つかりません")
            
            
            
        if context.scene.my_tool.org_obj in bpy.data.objects:
            # オブジェクトを選択してアクティブに設定
            org_obj = bpy.data.objects[context.scene.my_tool.org_obj]
            org_obj.select_set(True)
            #bpy.context.view_layer.objects.active = org_obj
        
        else:
            print("happysocks_outオブジェクトが見つかりません")
        

        if bpy.context.scene.render.engine == 'CYCLES':
            self.report({'INFO'}, 'BAKE')
            bpy.ops.object.bake(
                type=bpy.context.scene.cycles.bake_type,
                pass_filter={'COLOR'},
                use_selected_to_active=bpy.context.scene.render.bake.use_selected_to_active,
                save_mode='INTERNAL'  # 内部イメージに保存
            )
        return {'FINISHED'}


# =======================================================================
# パネル(メニュー)の定義
class SimplePanel(bpy.types.Panel):
    bl_label = "オレのデシメき手順"
    bl_idname = "OBJECT_PT_simple"
    bl_space_type = 'VIEW_3D'  # 3Dビューに表示
    bl_region_type = 'UI'      # サイドパネルに表示
    bl_category = "decimate_steper"    # タブの名前

    def draw(self, context):
        scene = context.scene
        props = scene.my_tool
        
        layout = self.layout
        
        row = layout.row()
        row.label(text="====オブジェクトをコピー====")
        
        row = layout.row()
        row.operator("object.simple_operator")
        layout.prop(props, "org_obj")
        layout.prop(props, "copied_obj")
        
        row = layout.row()
        row.operator("object.meshcleanup")
        row = layout.row()
        row.operator("object.deleteloose")
        
        layout.label(text="====デシメートあてる====")
        row = layout.row()
        row.operator("object.decimatepaneoperator")
        
        row = layout.row()
        row.label(text="====テクスチャ作成====")
        row = layout.row()
        row.operator("object.gettexturenameoperator")
        layout.prop(props, "Texturesize")
        layout.prop(props, "newTexturename")
        row = layout.row()
        row.label(text="1024 x ")
        layout.prop(props, "texsize", slider=True)
        row = layout.row()
        row.operator("object.texturecreatoperator")
        
        row = layout.row()
        row.label(text="====マテリアル新規作成====")
        row = layout.row()
        row.operator("object.materialoperator")
        
        row = layout.row()
        row.label(text="====Smart UV 展開====")
        row = layout.row()
        row.operator("object.smartuvoperator")
        
        row = layout.row()
        row.label(text="====テクスチャベイク====")
        row = layout.row()
        row.operator("object.texturebakeoperator")
        row = layout.row()
        row.operator("object.texturebakestart")


# =======================================================================
# クラスのリスト
classes = (
    MyAddonProperties,
    SimpleOperator,
    DecimatePaneOperator,
    GetTextureNameOperator,
    TextureCreateOperator,
    SmartUVOperator,
    MaterialOperator,
    TextureBakeOperator,
    TextureBakeStart,
    MeshMergebyDistance,
    MeshDeleteLoose,
    SimplePanel,
)




# =======================================================================
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # プロパティグループをシーンに登録
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyAddonProperties)
# =======================================================================
def unregister():
    # プロパティグループの登録解除
    del bpy.types.Scene.my_tool
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# スクリプトを直接実行した場合に登録を行う
if __name__ == "__main__":
    register()