export default function SearchBar() {
    return (
        <div className="input-group input-group-lg">
            <input
                type="text"
                className="form-control"
                placeholder="Search researchers, publications..."
            />

            <button className="btn btn-light">
                Search
            </button>
        </div>
    );
}
