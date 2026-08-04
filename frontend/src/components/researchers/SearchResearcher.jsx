export default function SearchResearcher({ search, setSearch }) {
    return (
        <input
            type="text"
            className="form-control"
            placeholder="Search researchers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
        />
    );
}
