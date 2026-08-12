import { BUILDER_TITLES } from "../constants";

export default function BuilderFields({ builder, onChange }) {
  const fields = [
    ["name", "Name", "e.g. Ramzan"],
    ["role", "Role", "e.g. Backend engineer"],
    ["stack", "Stack", "e.g. MERN · AI · Web3"],
  ];

  return (
    <fieldset className="builder-fields">
      <legend>Builder details</legend>
      {fields.map(([key, label, placeholder]) => (
        <label key={key} className="field-label">
          <span>{label}</span>
          <input
            value={builder[key]}
            onChange={(event) => onChange(key, event.target.value)}
            placeholder={placeholder}
            maxLength={key === "stack" ? 56 : 38}
          />
        </label>
      ))}
      <label className="field-label">
        <span>Builder title</span>
        <select value={builder.builderTitle} onChange={(event) => onChange("builderTitle", event.target.value)}>
          {BUILDER_TITLES.map((title) => <option key={title}>{title}</option>)}
        </select>
      </label>
    </fieldset>
  );
}
