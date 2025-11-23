import { PopularBooks } from "../components/PopularBooks";

export default function Home() {

  return (
    <div>
      <section className="mt-8 py-12 min-h-[566px] bg-[#E6EFF5] text-white">
        <div className="flex flex-col items-center text-center px-4">
          <h1 className="text-5xl font-bold leading-tight">
            Find Your Next Favorite Book or<br />
            Movie – Just for You!
          </h1>
          <h2 className="mt-5 text-lg max-w-3xl">
            Discover top-rated books and films, carefully selected to match your unique taste — from everyday
            favorites to hidden gems.
          </h2>
          <div className="my-8 max-w-4xl w-full">
            <img src="/promo.png" alt="Books" className="w-full object-cover rounded-lg shadow-lg" />
          </div>
          <div className="flex items-center space-x-4">
            <button className="btn-secondary text-sm px-6 py-2 rounded border border-white hover:bg-white hover:text-[#003B4A] transition">
              Login
            </button>
            <button className="btn-primary text-sm px-6 py-2 rounded bg-white text-[#003B4A] hover:bg-gray-200 transition">
              Register
            </button>
          </div>
        </div>
      </section>

      <PopularBooks/>




    </div>
  );
}
