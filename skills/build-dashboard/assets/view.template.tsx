import React from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";

export default function Dashboard({ data, metadata }) {
  return (
    <div style={{ width: "100%", height: 320 }}>
      <h1>{String(metadata?.title ?? "Dashboard")}</h1>
      <ResponsiveContainer>
        <BarChart data={data.<dataset_key> ?? []}>
          <XAxis dataKey="<x_field>" />
          <YAxis />
          <Bar dataKey="<y_field>" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
