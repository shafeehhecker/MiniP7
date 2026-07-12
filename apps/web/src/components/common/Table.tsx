import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  align?: "left" | "right";
}

interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export function Table<T>({ columns, rows, rowKey, onRowClick, emptyMessage = "Nothing here yet." }: TableProps<T>) {
  if (rows.length === 0) {
    return <p className="px-4 py-6 text-center text-sm text-steel">{emptyMessage}</p>;
  }
  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-paper-line">
          {columns.map((col) => (
            <th
              key={col.key}
              className={`px-3 py-2 font-mono text-[11px] uppercase tracking-wide text-steel ${
                col.align === "right" ? "text-right" : "text-left"
              }`}
            >
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr
            key={rowKey(row)}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            className={`border-b border-paper-line last:border-0 ${
              onRowClick ? "cursor-pointer hover:bg-paper" : ""
            }`}
          >
            {columns.map((col) => (
              <td
                key={col.key}
                className={`px-3 py-2 text-graphite ${col.align === "right" ? "text-right" : "text-left"}`}
              >
                {col.render(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
