"""
资产管理和知识库 API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import re
import shutil
import json
from pathlib import Path
from datetime import datetime

# 资产存储目录
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

# 元数据文件
METADATA_FILE = ASSETS_DIR / "metadata.json"


class AssetMetadata(BaseModel):
    """资产元数据"""
    filename: str
    character_name: str
    view_type: str
    file_path: str
    upload_time: str
    file_size: int


def load_metadata() -> Dict:
    """加载元数据"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"assets": []}


def save_metadata(metadata: Dict):
    """保存元数据"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def parse_filename(filename: str) -> tuple[str, str]:
    """
    解析文件名，提取人物名称和视图类型
    格式：人物名-视图类型.扩展名
    例如：小明-正视图.jpg -> ("小明", "正视图")
         小美-侧视图.png -> ("小美", "侧视图")
    """
    # 移除扩展名
    name_without_ext = Path(filename).stem
    
    # 使用正则表达式匹配：人物名-视图类型
    match = re.match(r'^(.+?)-(.+)$', name_without_ext)
    
    if match:
        character_name = match.group(1).strip()
        view_type = match.group(2).strip()
        return character_name, view_type
    else:
        # 如果没有匹配到，使用文件名作为人物名，视图类型为"未知"
        return name_without_ext, "未知"


def get_assets_by_character() -> Dict[str, List[AssetMetadata]]:
    """按人物分组获取资产"""
    metadata = load_metadata()
    assets_by_character: Dict[str, List[AssetMetadata]] = {}
    
    for asset_data in metadata.get("assets", []):
        asset = AssetMetadata(**asset_data)
        character = asset.character_name
        
        if character not in assets_by_character:
            assets_by_character[character] = []
        assets_by_character[character].append(asset)
    
    return assets_by_character


async def upload_asset(file: UploadFile) -> AssetMetadata:
    """上传资产文件"""
    # 检查文件类型
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。支持的格式：{', '.join(allowed_extensions)}"
        )
    
    # 解析文件名
    character_name, view_type = parse_filename(file.filename)
    
    # 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{character_name}-{view_type}_{timestamp}{file_ext}"
    file_path = ASSETS_DIR / safe_filename
    
    # 保存文件
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    # 创建元数据
    asset = AssetMetadata(
        filename=file.filename,
        character_name=character_name,
        view_type=view_type,
        file_path=str(file_path),
        upload_time=datetime.now().isoformat(),
        file_size=len(content)
    )
    
    # 保存元数据
    metadata = load_metadata()
    metadata["assets"].append(asset.dict())
    save_metadata(metadata)
    
    return asset


def delete_asset(filename: str) -> bool:
    """删除资产"""
    metadata = load_metadata()
    assets = metadata.get("assets", [])
    
    # 查找并删除
    for i, asset_data in enumerate(assets):
        asset = AssetMetadata(**asset_data)
        if asset.filename == filename or Path(asset.file_path).name == filename:
            # 删除文件
            file_path = Path(asset.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # 删除元数据
            assets.pop(i)
            save_metadata(metadata)
            return True
    
    return False


def get_asset_path(filename: str) -> Optional[Path]:
    """获取资产文件路径"""
    metadata = load_metadata()
    for asset_data in metadata.get("assets", []):
        asset = AssetMetadata(**asset_data)
        stored_filename = Path(asset.file_path).name
        # 匹配原始文件名或存储的文件名（支持部分匹配，因为存储时添加了时间戳）
        if (asset.filename == filename or 
            stored_filename == filename or 
            filename in stored_filename or
            stored_filename.startswith(filename.replace(Path(filename).suffix, ''))):
            path = Path(asset.file_path)
            if path.exists():
                return path
    return None

