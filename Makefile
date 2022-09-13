VERSION="1.0.0"


create-image:
	docker build -t seiscore:$(VERSION) .


upload-image:
	docker build -t ghcr.io/mikkoartik/seiscore:$(VERSION) .
	docker push ghcr.io/mikkoartik/seiscore:$(VERSION)


load-image:
	docker pull ghcr.io/mikkoartik/seiscore:$(VERSION)
