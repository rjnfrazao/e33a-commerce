# Auctions Application

### Design decisions

- Some operations related to the Auction Item page, such as watchlist add/remove and Closed auction, are using the same view where a url parameter is added: url\<operation>\<id_auction>, where operation is Add, Delete, or Close. Therefore we use the GET method to know operation and auction.
- The comments and place bid have their own view to process the post.
- The messages are divided in Error message and Alert message. Error message means somethins really wrong (like auction doesn't exist) and alert message display business messages. The alert messages are stores in session variable, so when the redirect is required the auction_item view knows which alert message should be displayed.
- The view file is getting big, maybe worthwhile check how to split in two or more views files.
- Index page makes use of parameters to decide if displays : Active or Closed auctions, or auctions from a specific category.
- Improve look and feel on Sun

### Requirements done

- Django Admin Interface on Mon.
- Place a Bid and check if higher than other bids on Wed.
- Watchlist Add and remove / Create the Watchlist model on Tue.
- List comments on Thur
- Add a comment on Thur
- List of closed auctions on Thur
- Bug: Not able to create decimal amount for the bid. on Thur
- Watchlist page on Fri
- Categories list \*> access all auctions from the category selected. on Fri
- page should inform when the user is the winner, list of closed auctions. on Fri
- Bug : Auction Item page : Category code displayed instead of catgory name. on Sun
- Bug : Select box for the category. on Sun
- Bug : Find out why the auction all object displays the username at the field I expected id user. Lack of knowledge on a Django concept. -> It seems django requires the objects to search on foreign keys.

### Bugs open

- When opened two browser, the session of the loged user appears at the browser where the user is not logged. Open page Auction Item (or detail) the user name is displayed.
  ao abrir o detalhe do auction, o usuário do outro browser aparece logado.
- Can´t display two lines for the auction´s description. Bootstrap issue or wrong html attribute?
