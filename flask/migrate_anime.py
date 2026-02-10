import json
import os
from app import app, db
from app.models.anime import Anime, Genre




def do_migrate_anime():
   path = os.path.join(app.root_path, 'data', 'anime_list.json')
   if not os.path.exists(path):
       print(f"File not found: {path}")
       return


   with open(path, 'r', encoding='utf-8') as f:
       anime_list = json.load(f)


   for item in anime_list:
       mal_id = item.get('mal_id')
       if not mal_id:
           continue
      
       if Anime.query.filter_by(mal_id=mal_id).first():
           print(f"Skipping {item.get('title_english') or item.get('title')}"
                 f" (already in DB)")
           continue


       print(f"Migrating {item.get('title_english') or item.get('title')}...")
       anime = Anime(
           mal_id=mal_id,
           title_english=item.get('title_english') or item.get('title'),
           image_url=item.get('image_url'),
           year=(item.get('year')
                 if item.get('year') != 'N/A' else None),
           episodes=(item.get('episodes')
                     if item.get('episodes') != 'N/A' else None),
           synopsis=item.get('synopsis'),
           score=(item.get('score')
                  if item.get('score') != 'N/A' else 0.0),
           my_rating=item.get('my_rating') or 0,
           deleted_at=None
       )
       # Add to session first to avoid SAWarning when appending relationships
       db.session.add(anime)
      
       # Handle genres
       genres = item.get('genres', [])
       for g_name in genres:
           if not g_name: continue
           genre = Genre.query.filter_by(name=g_name).first()
           if not genre:
               genre = Genre(name=g_name)
               db.session.add(genre)
           anime.genres.append(genre)
  
   db.session.commit()
   print("Migration complete!")


if __name__ == '__main__':
   with app.app_context():
       do_migrate_anime()