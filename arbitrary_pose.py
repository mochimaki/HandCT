"""
HandCT pose -> Export (STL / GLB / FBX)  **Blender 4.4.3対応・アドオン不要・ポーズ可変版**

■ 概要
- HandCTの手メッシュに任意のポーズを与え、変形を焼いた静的メッシュを書き出します。
- 出力形式は "STL"（3Dプリント用） / "FBX"（Fusion360向け） / "GLB"（Web共有用）を選択可能。
- 指の曲げ具合を冒頭で指定できるように設計されており、誰でも簡単にポーズを変更できます。
- 外部アドオン不要（Blender標準機能のみで動作）。

■ 使い方
1) HandCTの base_model.blend を開く
2) 「Scripting」タブ → テキストエディタで本スクリプトを貼り付け
3) 「ユーザー設定」欄の OUT_DIR / EXPORT_FORMAT を必要に応じて変更（"STL" / "GLB" / "FBX"）
4) ▶ 実行

■ 動作確認環境
- Blender 4.4.3 (Windows 11)
- HandCT Dataset (DOI: 10.5281/zenodo.6473101)
"""

import bpy, os, traceback

# ========= ユーザー設定 =========
OUT_DIR = r"C:\Temp\HandCT_02\out_pose"   # 出力フォルダ
EXPORT_FORMAT = "STL"                     # "STL" / "GLB" / "FBX"
FILENAME_BASE = "custom_pose"             # 出力ファイル名ベース

# 指の開閉度（0=曲げる, 1=開く）
POSE = {
    "thumb": 1.0,     # 親指
    "index": 1.0,     # 人差し指
    "middle": 0.1,    # 中指
    "ring": 1.0,      # 薬指
    "pinky": 0.1      # 小指
}
# =================================

def log(msg): print("[HandCT]", msg)
def ensure_outdir(p): os.makedirs(p, exist_ok=True)

def get_hand_and_armature():
    hand = bpy.data.objects.get("Hand Ok")
    if hand and hand.type != 'MESH':
        hand = None
    if not hand:
        for o in bpy.data.objects:
            if o.type == 'MESH':
                for m in o.modifiers:
                    if m.type == 'ARMATURE' and m.object:
                        hand = o; break
            if hand: break
    if not hand:
        raise RuntimeError("Armatureモディファイア付きのメッシュが見つかりません。")
    arm = next((m.object for m in hand.modifiers if m.type == 'ARMATURE' and m.object), None)
    if not arm:
        raise RuntimeError("Armatureオブジェクトが見つかりません。")
    return hand, arm

def apply_pose(arm):
    """POE変数に基づいて指の開閉を設定"""
    B = arm.pose.bones
    CTL = {
        "index": "palm.01.L.001",
        "middle": "palm.02.L.001",
        "ring": "palm.03.L.001",
        "pinky": "palm.04.L.001",
    }
    THB = "thumb.01.L.001"
    def clamp(x,a,b): return max(a, min(b, x))
    Y_MIN, Y_MAX = 0.5, 1.5
    def set_open(ctrl_name, open01):
        y = Y_MIN + clamp(open01,0,1)*(Y_MAX-Y_MIN)
        if ctrl_name in B:
            sx, _, sz = B[ctrl_name].scale
            B[ctrl_name].scale = (sx, y, sz)
    set_open(CTL["index"],  POSE["index"])
    set_open(CTL["middle"], POSE["middle"])
    set_open(CTL["ring"],   POSE["ring"])
    set_open(CTL["pinky"],  POSE["pinky"])
    set_open(THB,           POSE["thumb"])

def make_baked_mesh(hand):
    deps = bpy.context.evaluated_depsgraph_get()
    eval_obj = hand.evaluated_get(deps)
    mesh = bpy.data.meshes.new_from_object(eval_obj, preserve_all_data_layers=True, depsgraph=deps)
    temp_obj = bpy.data.objects.new("HandExportTemp", mesh)
    bpy.context.scene.collection.objects.link(temp_obj)
    for o in bpy.context.selected_objects: o.select_set(False)
    temp_obj.select_set(True)
    bpy.context.view_layer.objects.active = temp_obj
    return temp_obj

def detect_stl_operator():
    if hasattr(bpy.ops, "wm") and "stl_export" in dir(bpy.ops.wm): return "wm"
    if hasattr(bpy.ops, "export_mesh") and "stl" in dir(bpy.ops.export_mesh): return "export_mesh"
    return None
"""
export_selection関数は、STL、GLB、FBXの3つの形式に対応しています。
STLのエクスポーターはBlenderのバージョンによって異なるため、detect_stl_operator関数で判定し、適切なエクスポーターを使用します。
■ Blender 4.x のSTLエクスポート変更点（重要）
- 旧:  `bpy.ops.export_mesh.stl(...)`  …… Blender 3.x系から存在。`use_selection=True`, `ascii=False` などを受け付ける。
- 新:  `bpy.ops.wm.stl_export(...)`    …… Blender 4.x系で導入。
    - **`use_selection` → 廃止**（代わりに `export_selected_objects=True`）
    - **`ascii` → 廃止**（代わりに `ascii_format=False`）
  → 新版では、エクスポート前に「書き出したいオブジェクトのみを選択」し、`export_selected_objects=True` を指定する運用に変更。

export_selection関数は環境を自動判別して、
  - 新版が使える場合: `wm.stl_export`（`ascii_format`, `export_selected_objects` を使用）
  - 旧版のみの場合:   `export_mesh.stl`（`ascii`, `use_selection` を使用）
という二経路に自動対応します。
"""
def export_selection(out_dir, basename, fmt):
    fmt = fmt.upper()
    if fmt == "GLB":
        path = os.path.join(out_dir, f"{basename}.glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_materials='EXPORT', export_yup=True)
    elif fmt == "STL":
        path = os.path.join(out_dir, f"{basename}.stl")
        op = detect_stl_operator()
        if op == "wm": # 新エクスポーター
            bpy.ops.wm.stl_export(filepath=path, export_selected_objects=True, ascii_format=False, use_scene_unit=True, apply_modifiers=True)
        else: # 旧エクスポーター
            bpy.ops.export_mesh.stl(filepath=path, use_selection=True, ascii=False, use_scene_unit=True)
    elif fmt == "FBX":
        path = os.path.join(out_dir, f"{basename}.fbx")
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True, add_leaf_bones=False, bake_space_transform=True)
    else:
        raise ValueError("Unsupported format")
    return path

def main():
    log(f"START ({EXPORT_FORMAT})")
    ensure_outdir(OUT_DIR)
    hand, arm = get_hand_and_armature()
    apply_pose(arm)
    bpy.context.view_layer.update()
    temp_obj = make_baked_mesh(hand)
    try:
        path = export_selection(OUT_DIR, FILENAME_BASE, EXPORT_FORMAT)
        log(f"Exported: {path}")
    finally:
        temp_obj.select_set(True)
        bpy.ops.object.delete()

if __name__ == "__main__":
    try: main()
    except Exception as e:
        log("ERROR: " + str(e))
        traceback.print_exc()
