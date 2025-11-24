#!/usr/bin/env python3
"""
Excel Processor v4 PRO para 賃金台帳 Generator
- Procesa archivos 勤怠表
- Guarda en base de datos SQLite
- Genera reportes consolidados
"""

from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from datetime import datetime
import os
import re
import json

# Importar módulo de base de datos
from database import (
    init_database, save_payroll_record, get_all_payroll_records,
    get_payroll_by_employee, get_payroll_by_period, get_periods,
    get_all_employees, log_audit, check_auto_backup
)


class ExcelProcessor:
    """Procesa archivos de 勤怠表 y guarda en base de datos"""
    
    COLUMN_MAP = {
        "number": 0,
        "employee_id": 1,
        "name_roman": 2,
        "name_jp": 3,
        "period": 4,
        "period_start": 5,
        "period_end": 6,
        "work_days": 7,
        "holiday_work_days": 8,
        "absence_days": 9,
        "paid_leave_days": 10,
        "special_leave_days": 11,
        "work_hours": 12,
        "overtime_hours": 13,
        "holiday_hours": 14,
        "night_hours": 15,
        "hourly_rate": 16,
        "base_pay": 17,
        "overtime_pay": 18,
        "night_pay": 19,
        "holiday_pay": 20,
        "paid_leave_pay": 21,
        "total_pay": 31,
        "health_insurance": 32,
        "pension": 33,
        "employment_insurance": 34,
        "social_total": 35,
        "resident_tax": 36,
        "income_tax": 37,
        "deduction_total": 47,
        "net_pay": 48,
    }
    
    HEADERS_JP = [
        "Number", "従業員番号", "氏名ローマ字", "氏名", "支給分",
        "賃金計算期間開始", "賃金計算期間終了", "出勤日数", "休日出勤日数", "欠勤日数",
        "有休日数", "特別休暇日数", "実働時間", "残業時間数", "休日労働時間数",
        "深夜労働時間数", "基本給(時給)", "基本給金額", "残業手当", "深夜手当",
        "休日勤務手当", "有給休暇", "手当1", "手当2", "手当3",
        "手当4", "手当5", "手当6", "手当7", "手当8",
        "前月給与", "合計", "健康保険料", "厚生年金", "雇用保険料",
        "社会保険料計", "住民税", "所得税", "控除1", "控除2",
        "控除3", "控除4", "控除5", "控除6", "控除7",
        "控除8", "控除9", "控除合計", "差引支給額", "通勤手当(非)",
        "その他手当1", "その他"
    ]
    
    def __init__(self):
        self.processed_files = []
        self.errors = []
        self.records_saved = 0
        
        # Inicializar base de datos
        init_database()
        
        # Verificar backup automático
        check_auto_backup()
    
    def process_file(self, filepath: str) -> dict:
        """Procesa un archivo Excel y guarda en BD"""
        filename = os.path.basename(filepath)
        
        try:
            wb = load_workbook(filepath, data_only=True)
            
            # Buscar hoja de datos
            sheet_name = None
            for name in wb.sheetnames:
                if any(x in name for x in ["給料明細", "給料", "明細", "Sheet1"]):
                    sheet_name = name
                    break
            
            if not sheet_name:
                sheet_name = wb.sheetnames[0]
            
            ws = wb[sheet_name]
            records_count = 0
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not row or not row[1]:
                    continue
                
                employee_id = str(row[1]) if row[1] else None
                if not employee_id or employee_id.lower() in ["none", ""]:
                    continue
                
                # Construir registro
                record = {
                    "source_file": filename,
                    "employee_id": employee_id,
                    "name_roman": row[2] if len(row) > 2 else None,
                    "name_jp": row[3] if len(row) > 3 else None,
                    "period": row[4] if len(row) > 4 else None,
                    "period_start": self._format_date(row[5]) if len(row) > 5 else None,
                    "period_end": self._format_date(row[6]) if len(row) > 6 else None,
                    "work_days": self._to_number(row[7]) if len(row) > 7 else 0,
                    "work_hours": self._to_number(row[12]) if len(row) > 12 else 0,
                    "overtime_hours": self._to_number(row[13]) if len(row) > 13 else 0,
                    "holiday_hours": self._to_number(row[14]) if len(row) > 14 else 0,
                    "night_hours": self._to_number(row[15]) if len(row) > 15 else 0,
                    "hourly_rate": self._to_number(row[16]) if len(row) > 16 else 0,
                    "base_pay": self._to_number(row[17]) if len(row) > 17 else 0,
                    "overtime_pay": self._to_number(row[18]) if len(row) > 18 else 0,
                    "night_pay": self._to_number(row[19]) if len(row) > 19 else 0,
                    "holiday_pay": self._to_number(row[20]) if len(row) > 20 else 0,
                    "total_pay": self._to_number(row[31]) if len(row) > 31 else 0,
                    "health_insurance": self._to_number(row[32]) if len(row) > 32 else 0,
                    "pension": self._to_number(row[33]) if len(row) > 33 else 0,
                    "employment_insurance": self._to_number(row[34]) if len(row) > 34 else 0,
                    "income_tax": self._to_number(row[37]) if len(row) > 37 else 0,
                    "resident_tax": self._to_number(row[36]) if len(row) > 36 else 0,
                    "deduction_total": self._to_number(row[47]) if len(row) > 47 else 0,
                    "net_pay": self._to_number(row[48]) if len(row) > 48 else 0,
                }
                
                # Guardar en base de datos
                save_payroll_record(record)
                records_count += 1
                self.records_saved += 1
            
            wb.close()
            
            # Log de auditoría
            log_audit('PROCESS_FILE', 'processed_files', filename, None, None,
                      f"Procesados {records_count} registros")
            
            self.processed_files.append({
                "filename": filename,
                "records": records_count,
                "status": "success"
            })
            
            return {"status": "success", "records": records_count}
            
        except Exception as e:
            error_msg = f"Error procesando {filename}: {str(e)}"
            self.errors.append(error_msg)
            log_audit('PROCESS_FILE_ERROR', 'processed_files', filename, None, None, str(e))
            
            self.processed_files.append({
                "filename": filename,
                "records": 0,
                "status": "error",
                "error": str(e)
            })
            
            return {"status": "error", "message": str(e)}
    
    def _format_date(self, value):
        """Formatear fecha a string"""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return str(value) if value else None
    
    def _to_number(self, value):
        """Convertir a número"""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return value
        try:
            return float(str(value).replace(",", "").replace("¥", ""))
        except:
            return 0
    
    def get_all_data(self) -> list:
        """Obtener todos los datos de la BD"""
        return get_all_payroll_records()
    
    def get_summary(self) -> dict:
        """Obtener resumen"""
        records = get_all_payroll_records()
        employees = get_all_employees()
        periods = get_periods()
        
        return {
            "total_records": len(records),
            "unique_employees": len(employees),
            "periods": periods,
            "processed_files": self.processed_files,
            "errors": self.errors,
            "records_saved_this_session": self.records_saved
        }
    
    def export_to_excel_all(self, output_path: str) -> str:
        """Exportar todos los datos a Excel ALL"""
        records = get_all_payroll_records()
        
        wb = Workbook()
        ws = wb.active
        ws.title = "ALL"
        
        # Headers
        header_fill = PatternFill("solid", fgColor="4472C4")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        
        for col, header in enumerate(self.HEADERS_JP, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        
        # Datos
        for row_idx, record in enumerate(records, 2):
            ws.cell(row=row_idx, column=1, value=row_idx - 1)
            ws.cell(row=row_idx, column=2, value=record.get('employee_id'))
            ws.cell(row=row_idx, column=3, value=record.get('name_roman'))
            ws.cell(row=row_idx, column=4, value=record.get('name_jp'))
            ws.cell(row=row_idx, column=5, value=record.get('period'))
            ws.cell(row=row_idx, column=6, value=record.get('period_start'))
            ws.cell(row=row_idx, column=7, value=record.get('period_end'))
            ws.cell(row=row_idx, column=8, value=record.get('work_days'))
            ws.cell(row=row_idx, column=13, value=record.get('work_hours'))
            ws.cell(row=row_idx, column=14, value=record.get('overtime_hours'))
            ws.cell(row=row_idx, column=15, value=record.get('holiday_hours'))
            ws.cell(row=row_idx, column=16, value=record.get('night_hours'))
            ws.cell(row=row_idx, column=18, value=record.get('base_pay'))
            ws.cell(row=row_idx, column=19, value=record.get('overtime_pay'))
            ws.cell(row=row_idx, column=20, value=record.get('night_pay'))
            ws.cell(row=row_idx, column=21, value=record.get('holiday_pay'))
            ws.cell(row=row_idx, column=32, value=record.get('total_pay'))
            ws.cell(row=row_idx, column=33, value=record.get('health_insurance'))
            ws.cell(row=row_idx, column=34, value=record.get('pension'))
            ws.cell(row=row_idx, column=35, value=record.get('employment_insurance'))
            ws.cell(row=row_idx, column=38, value=record.get('income_tax'))
            ws.cell(row=row_idx, column=48, value=record.get('deduction_total'))
            ws.cell(row=row_idx, column=49, value=record.get('net_pay'))
            
            # Formato moneda
            for col in [18, 19, 20, 21, 32, 33, 34, 35, 38, 48, 49]:
                ws.cell(row=row_idx, column=col).number_format = '#,##0'
        
        wb.save(output_path)
        log_audit('EXPORT_ALL', None, None, None, None, f"Exportado a {output_path}")
        
        return output_path
    
    def export_by_month(self, output_path: str) -> str:
        """Exportar con hojas separadas por mes"""
        records = get_all_payroll_records()
        
        wb = Workbook()
        wb.remove(wb.active)
        
        # Agrupar por periodo
        by_period = {}
        for record in records:
            period = record.get("period", "Unknown")
            if period not in by_period:
                by_period[period] = []
            by_period[period].append(record)
        
        header_fill = PatternFill("solid", fgColor="4472C4")
        header_font = Font(bold=True, color="FFFFFF", size=10)
        
        for period, period_records in sorted(by_period.items()):
            sheet_name = period[:31].replace("/", "-").replace("\\", "-")
            ws = wb.create_sheet(title=sheet_name)
            
            # Headers
            for col, header in enumerate(self.HEADERS_JP, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.fill = header_fill
                cell.font = header_font
            
            # Datos
            for row_idx, record in enumerate(period_records, 2):
                ws.cell(row=row_idx, column=1, value=row_idx - 1)
                ws.cell(row=row_idx, column=2, value=record.get('employee_id'))
                ws.cell(row=row_idx, column=3, value=record.get('name_roman'))
                ws.cell(row=row_idx, column=4, value=record.get('name_jp'))
                ws.cell(row=row_idx, column=5, value=record.get('period'))
                ws.cell(row=row_idx, column=32, value=record.get('total_pay'))
                ws.cell(row=row_idx, column=49, value=record.get('net_pay'))
        
        # Hoja ALL
        ws_all = wb.create_sheet(title="ALL")
        for col, header in enumerate(self.HEADERS_JP, 1):
            cell = ws_all.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
        
        for row_idx, record in enumerate(records, 2):
            ws_all.cell(row=row_idx, column=2, value=record.get('employee_id'))
            ws_all.cell(row=row_idx, column=3, value=record.get('name_roman'))
            ws_all.cell(row=row_idx, column=5, value=record.get('period'))
            ws_all.cell(row=row_idx, column=32, value=record.get('total_pay'))
            ws_all.cell(row=row_idx, column=49, value=record.get('net_pay'))
        
        wb.save(output_path)
        log_audit('EXPORT_BY_MONTH', None, None, None, None, f"Exportado a {output_path}")
        
        return output_path
    
    def export_chingin_by_employee(self, output_folder: str) -> list:
        """Exportar 賃金台帳 individual por empleado"""
        os.makedirs(output_folder, exist_ok=True)
        
        employees = get_all_employees()
        generated_files = []
        
        for emp in employees:
            emp_id = emp['employee_id']
            records = get_payroll_by_employee(emp_id)
            
            if not records:
                continue
            
            wb = Workbook()
            ws = wb.active
            ws.title = "賃金台帳"
            
            # Título
            ws['B2'] = f"賃金台帳 - {datetime.now().year}年"
            ws['B2'].font = Font(bold=True, size=16)
            
            # Info empleado
            ws['B4'] = "従業員番号"
            ws['C4'] = emp_id
            ws['B5'] = "氏名"
            ws['C5'] = emp.get('name_jp', records[0].get('name_jp', ''))
            ws['B6'] = "氏名ローマ字"
            ws['C6'] = emp.get('name_roman', records[0].get('name_roman', ''))
            
            # Headers de meses
            row = 9
            headers = ["項目", "1月", "2月", "3月", "4月", "5月", "6月",
                      "7月", "8月", "9月", "10月", "11月", "12月", "合計"]
            
            for col, h in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col, value=h)
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="E0E0E0")
            
            # Items
            items = [
                ("出勤日数", "work_days"),
                ("実働時間", "work_hours"),
                ("残業時間", "overtime_hours"),
                ("深夜時間", "night_hours"),
                ("基本給", "base_pay"),
                ("残業手当", "overtime_pay"),
                ("深夜手当", "night_pay"),
                ("総支給額", "total_pay"),
                ("健康保険", "health_insurance"),
                ("厚生年金", "pension"),
                ("雇用保険", "employment_insurance"),
                ("所得税", "income_tax"),
                ("控除合計", "deduction_total"),
                ("差引支給額", "net_pay")
            ]
            
            # Mapear por mes
            by_month = {}
            for rec in records:
                period = rec.get("period", "")
                match = re.search(r'(\d+)月', period)
                if match:
                    month = int(match.group(1))
                    by_month[month] = rec
            
            for item_idx, (item_name, field) in enumerate(items):
                r = row + item_idx + 1
                ws.cell(row=r, column=1, value=item_name)
                
                total = 0
                for month in range(1, 13):
                    col = month + 1
                    if month in by_month:
                        value = by_month[month].get(field, 0) or 0
                        ws.cell(row=r, column=col, value=value)
                        if isinstance(value, (int, float)):
                            total += value
                            ws.cell(row=r, column=col).number_format = '#,##0'
                
                ws.cell(row=r, column=14, value=total)
                ws.cell(row=r, column=14).number_format = '#,##0'
                ws.cell(row=r, column=14).font = Font(bold=True)
            
            # Guardar
            safe_name = emp_id.replace("/", "_").replace("\\", "_")
            filepath = os.path.join(output_folder, f"賃金台帳_{safe_name}.xlsx")
            wb.save(filepath)
            generated_files.append(filepath)
        
        log_audit('EXPORT_CHINGIN', None, None, None, None,
                  f"Exportados {len(generated_files)} archivos 賃金台帳")
        
        return generated_files
    
    def clear(self):
        """Limpiar datos de sesión"""
        self.processed_files = []
        self.errors = []
        self.records_saved = 0


# Test
if __name__ == "__main__":
    print("="*60)
    print("🧪 TEST: Excel Processor v4 PRO con Base de Datos")
    print("="*60)
    
    processor = ExcelProcessor()
    
    # Crear datos de prueba
    from create_test_data import employees_jan, employees_feb, create_kintai_file
    
    test_folder = "/home/claude/chingin_app_v4/test_files"
    output_folder = "/home/claude/chingin_app_v4/outputs"
    os.makedirs(test_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    # Procesar archivos de prueba
    test_files = [
        "/home/claude/chingin_test/test_files/従業員賃金計算用_202501.xlsx",
        "/home/claude/chingin_test/test_files/従業員賃金計算用_202502.xlsx"
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            result = processor.process_file(filepath)
            print(f"   ✓ {os.path.basename(filepath)}: {result}")
    
    # Resumen
    summary = processor.get_summary()
    print(f"\n📊 RESUMEN:")
    print(f"   Total registros en BD: {summary['total_records']}")
    print(f"   Empleados únicos: {summary['unique_employees']}")
    print(f"   Periodos: {summary['periods']}")
    print(f"   Guardados esta sesión: {summary['records_saved_this_session']}")
    
    # Exportar
    print("\n📥 Exportando...")
    processor.export_to_excel_all(os.path.join(output_folder, "ALL_v4.xlsx"))
    print("   ✓ ALL_v4.xlsx")
    
    processor.export_by_month(os.path.join(output_folder, "Por_mes_v4.xlsx"))
    print("   ✓ Por_mes_v4.xlsx")
    
    processor.export_chingin_by_employee(os.path.join(output_folder, "賃金台帳_v4"))
    print("   ✓ 賃金台帳 individuales")
    
    print("\n✅ TEST COMPLETADO!")
