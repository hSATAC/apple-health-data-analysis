import xml.etree.ElementTree as ET
from collections import Counter
import pandas as pd

def analyze_health_data_types(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # 統計各種健康記錄類型
    record_types = Counter()
    
    for record in root.findall('.//Record'):
        record_type = record.get('type')
        if record_type:
            record_types[record_type] += 1
    
    # 顯示所有記錄類型和數量
    print("健康數據類型統計：")
    print("-" * 60)
    
    df = pd.DataFrame(record_types.most_common(), columns=['類型', '記錄數'])
    print(df.to_string(index=False))
    
    return record_types

if __name__ == "__main__":
    # 分析兩個 XML 檔案
    print("\n=== 分析 export_cda.xml ===")
    types1 = analyze_health_data_types('export_cda.xml')
    
    print("\n\n=== 分析 輸出.xml ===")
    types2 = analyze_health_data_types('輸出.xml')